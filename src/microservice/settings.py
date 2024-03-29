import os

from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
HOSTNAME_EXTERNAL = os.getenv('HOSTNAME_EXTERNAL')
PORT_EXTERNAL = os.getenv('PORT_EXTERNAL')
ENDPOINT_URL = f'{HOSTNAME_EXTERNAL}:{PORT_EXTERNAL}'
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")
RABBIT_STATISTIC_QUEUE = os.getenv("RABBIT_STATISTIC_QUEUE")

SECRET_KEY = os.getenv("SECRET_KEY")
AUTH_HEADER_PREFIX = 'Bearer '
ACCESS_TOKEN_KEY = SECRET_KEY
JWT_ALGORITHM = 'HS256'
