import logging
import os
import io
import uuid

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


class LocalstackManager:
    @staticmethod
    def get_credentials():
        """
        Get credentials from .env
        """
        credentials = {
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_KEY'),
            'region_name': os.getenv('REGION_NAME'),
            'endpoint_url': f'{os.getenv("HOSTNAME_EXTERNAL")}:'
                            f'{os.getenv("PORT_EXTERNAL")}'
        }
        return credentials

    @staticmethod
    def get_client(client_name):
        credentials = LocalstackManager.get_credentials()
        client = boto3.client(service_name=client_name, **credentials)
        return client

    @staticmethod
    def get_resource(resource_name):
        credentials = LocalstackManager.get_credentials()
        resource = boto3.resource(service_name=resource_name, **credentials)
        return resource

    @staticmethod
    def get_bucket(bucket_name):
        """
        Get if exists or create S3 bucket
        """
        client = LocalstackManager.get_client('s3')
        try:
            logger.info('Start creating bucket')
            bucket = client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': os.getenv('REGION_NAME')
                }
            )
            logger.info(str(bucket))
        except client.exceptions.BucketAlreadyOwnedByYou:
            resource = LocalstackManager.get_resource('s3')
            bucket = resource.Bucket(name=bucket_name)

        return bucket

    @staticmethod
    def upload_file(file):
        key = f'{uuid.uuid4()}.{file.name.rsplit(".")[-1]}'
        client = LocalstackManager.get_client('s3')
        try:
            client.upload_fileobj(Fileobj=file.file,
                                  Bucket=os.getenv('BUCKET_NAME'),
                                  Key=key)
        except ClientError as e:
            logger.error(e)
            raise
        return key

    @staticmethod
    def delete_file(url):
        if not url:
            return None

        key = LocalstackManager.get_key_from_url(url)
        client = LocalstackManager.get_client('s3')
        try:
            client.delete_object(Bucket=os.getenv('BUCKET_NAME'),
                                 Key=key)
        except ClientError as e:
            logger.error(e)
            raise

    @staticmethod
    def get_key_from_url(url):
        key = url.split(os.getenv('BUCKET_NAME') + '/')[1].split('?')[0]
        return key

    @staticmethod
    def create_presigned_url(key):
        bucket_name = os.getenv('BUCKET_NAME')

        client = LocalstackManager.get_client('s3')

        try:
            response = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name,
                        'Key': key},
                ExpiresIn=os.getenv('EXPIRATION_TIME')
            )
        except ClientError as e:
            logging.error(e)
            return None

        else:
            return response.replace('localstack', '0.0.0.0')
