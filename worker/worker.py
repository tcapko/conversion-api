#import redis
#from rq import Worker, Connection

# Establish Redis connection
#redis_url = 'redis://localhost:6379/0'
#conn = redis.from_url(redis_url)

#if __name__ == '__main__':
#    with Connection(conn):
#        worker = Worker('default')
#        worker.work()

from rq import Worker, Queue, Connection
from redis import Redis
import os

# Set up the Redis connection
redis_conn = Redis(host='localhost', port=6379)

if __name__ == '__main__':

    with Connection(redis_conn):
        worker = Worker(Queue('default'), connection=redis_conn)
        worker.work()

