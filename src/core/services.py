import logging
import uuid

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from page.models import Page

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
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'region_name': settings.REGION_NAME,
            'endpoint_url': f'{settings.HOSTNAME_EXTERNAL}:'
                            f'{settings.PORT_EXTERNAL}'
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
                    'LocationConstraint': settings.REGION_NAME
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
                                  Bucket=settings.BUCKET_NAME,
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
            client.delete_object(Bucket=settings.BUCKET_NAME,
                                 Key=key)
        except ClientError as e:
            logger.error(e)
            raise

    @staticmethod
    def get_key_from_url(url):
        key = url.split(settings.BUCKET_NAME + '/')[1]
        return key

    @staticmethod
    def create_object_url(key):
        url = f'http://0.0.0.0:{settings.PORT_EXTERNAL}/{settings.BUCKET_NAME}/{key}'
        return url

    @staticmethod
    def send_email(data):
        client = LocalstackManager.get_client('ses')
        page = Page.objects.prefetch_related('followers').get(id=data['page'])
        if not page.followers.all():
            return None
        email_list = list(page.followers.values_list('email', flat=True))
        user = page.owner
        subject = f'Innotter: {user.username} created a new post!'
        message = f'User {user.username} created a new post: {data["content"]}'
        response = client.send_email(
            Source=settings.EMAIL_HOST_USER,
            Destination={
                'ToAddresses': email_list,
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': message,
                    },
                }
            },
        )
        return response
