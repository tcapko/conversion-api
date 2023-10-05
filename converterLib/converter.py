import subprocess
import logging

# Configure the logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a stream handler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

def convert_to_pdf(file_path, job_id=None):
    pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
    try:
        logger.info("Trying PDF conversion...")
        # Run the command and capture the output
        result = subprocess.run(['unoconv', '-vvv', '--format=pdf', '--output', pdf_path, file_path], capture_output=True, text=True)

        # Log the command output
        # logger.info('>> Unoconv command output:  \n%s', result.stdout)
        # logger.info('>> Unoconv stderr output: \n%s', result.stderr)

        # Check the return code
        if result.returncode == 0:
            logger.info('Conversion to PDF successful')
            return pdf_path
        else:
            logger.error('Conversion to PDF failed')

    except Exception as e:
        logger.exception('An error occurred during conversion to PDF: %s', str(e))
