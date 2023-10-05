import sys
import logging
from flask import Flask, request, jsonify, send_file
from flask_restx import Api, Resource, fields
from rq import Queue
from rq.job import Job
#from worker import conn  # Redis connection
from redis import Redis
import subprocess
import os
from converter import convert_to_pdf

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  # Change the log level as needed

# Configure the logging in your app.py script
logging.basicConfig(level=logging.DEBUG)  # Set the log level to DEBUG
console_handler = logging.StreamHandler()  # Log messages to the console
app.logger.addHandler(console_handler)

# Set the log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

api = Api(app, version='1.0', title='File Conversion API', description='API endpoints for file conversion', doc='/swagger')


# Set up the Redis connection
conn = Redis(host='redis', port=6379)

# Set up the RQ queue
q = Queue(connection=conn)

# Check Redis connection
try:
    conn.ping()
except Exception as e:
    app.logger.error(f"Error connecting to Redis: {e}")
    exit(1)

# Check if unoconv is available
try:
    subprocess.run(['unoconv', '--version'], check=True, capture_output=True)
except Exception as e:
    app.logger.error(f"Error executing unoconv: {e}")
    exit(1)

q = Queue(connection=conn)

file_model = api.model('File', {
    'file': fields.Raw(description='The file to be converted.', format='binary'),
    'file_path': fields.String(description='The path of the file to be converted.')
})

convert_response_model = api.model('ConvertResponse', {
    'job_id': fields.String(description='The ID of the conversion job.')
})

class Convert(Resource):
    @api.expect(file_model)
    @api.response(202, 'Conversion job submitted', convert_response_model)
    @api.response(400, 'Bad Request')
    @api.doc(description='Converts a file to PDF format')
    def post(self):
        if 'file' in request.files:
            # File is provided as a multipart/form-data attachment
            file = request.files['file']
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
        elif 'file_path' in request.json:
            # File path is provided as a JSON field
            file_path = request.json['file_path']
            if not os.path.isfile(file_path):
                return {'error': 'Invalid file path'}, 400
        else:
            return {'error': 'No file or file path provided'}, 400

        # Enqueue the conversion task
        job = q.enqueue(convert_to_pdf, file_path)

        # Return a JSON response with the job ID
        return {'job_id': job.id}, 202

class Status(Resource):
    @api.doc(description='Retrieves the conversion status of a specific job')
    def get(self, job_id):
        job = Job.fetch(job_id, connection=conn)
        if job.is_finished:
            # Conversion is completed, return the PDF file
            pdf_path = job.result
            return jsonify({'status': 'finished'})
        else:
            # Conversion is still in progress
            return jsonify({'status': 'in progress'})


class Download(Resource):
    @api.doc(description='Retrieves the conversion status of a specific job')
    def get(self, job_id):
        # Check if the job exists and has a success status
        job = Job.fetch(job_id, connection=conn)

        if job is None:
            return jsonify({'error': 'Job not found'})

        if job.get_status() != 'finished':
            return jsonify({'error': 'Job status: ' + job.get_status()})

        # Assuming the PDF file path is stored as job.result
        pdf_file_path = job.result

        # Send the file for download
        return send_file(pdf_file_path, as_attachment=True)


api.add_resource(Convert, '/convert')
api.add_resource(Status, '/status/<job_id>')
api.add_resource(Download, '/download/<job_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

