import logging
import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import settings

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')
LAMBDA_ZIP = './lambda/lambda.zip'


class LocalstackManager:
    @staticmethod
    def __get_credentials():
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

    def _get_client(self, client_name):
        credentials = self.__get_credentials()
        client = boto3.client(service_name=client_name,
                              **credentials)
        return client

    def _get_resource(self, resource_name):
        credentials = self.__get_credentials()
        resource = boto3.resource(service_name=resource_name,
                                  **credentials)
        return resource


class LocalstackDynamoDB(LocalstackManager):
    def __init__(self):
        self.table = self.get_table()

    def get_table(self):
        resource = self._get_resource('dynamodb')
        client = self._get_client('dynamodb')

        try:
            logger.info('Trying to create table...')
            table = resource.create_table(
                TableName=settings.DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'page_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'page_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_uuid', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {'IndexName': 'user_uuid-index',
                     'KeySchema': [
                         {'AttributeName': 'user_uuid', 'KeyType': 'HASH'},
                         {'AttributeName': 'page_id', 'KeyType': 'RANGE'}],
                     'Projection': {'ProjectionType': 'ALL'},
                     'ProvisionedThroughput': {'ReadCapacityUnits': 5,
                                               'WriteCapacityUnits': 5}
                     }
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10,
                                       'WriteCapacityUnits': 10})
            logger.info('Table successfully created.')
        except client.exceptions.ResourceInUseException:
            logger.info('Table has already exists.')
            table = resource.Table(settings.DYNAMODB_TABLE_NAME)
            logger.info('Get table by name.')
        return table

    def query(self, user_uuid):
        table = self.get_table()
        items = table.query(
            IndexName='user_uuid-index',
            KeyConditionExpression=Key('user_uuid').eq(user_uuid))
        return items.get('Items', [])

    def delete_table(self):
        client = self._get_client('dynamodb')
        client.delete_table(TableName=settings.DYNAMODB_TABLE_NAME)

    def put_item(self, page_id: dict):
        response = self.table.put_item(Item=page_id)
        return response

    def get_item(self, page_id: str):
        try:
            response = self.table.get_item(Key={'page_id': page_id})
            return response.get('Item', [])
        except ClientError as e:
            logger.error(e.response['Error']['Message'])

    def delete_item(self, page_id: str):
        response = self.table.delete_item(
            Item={
                'page_id': page_id
            }
        )
        return response

    def update_item(self, page_id: str):
        response = self.table.update_item(
            Item={
                'page_id': page_id
            }
        )
        return response

    def get_all(self):
        response = self.table.scan()
        return response.get('Items', [])


class LocalstackLambda(LocalstackManager):
    @staticmethod
    def create_lambda_zip():
        """
        Generate ZIP file for lambda function.
        """
        # write down in console: zip -r lambda.zip .

    def create_lambda(self, function_name):
        """
        Creates a Lambda function in LocalStack.
        """
        try:
            lambda_client = self._get_client('lambda')
            with open(LAMBDA_ZIP, 'rb') as f:
                zipped_code = f.read()
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',
                Role='role',
                Handler=function_name + '.handler',
                Code=dict(ZipFile=zipped_code),
                Environment={
                    'Variables': {
                        'LOCALSTACK': 'True',
                        'AWS_ACCESS_KEY_ID': settings.AWS_ACCESS_KEY_ID,
                        'AWS_SECRET_ACCESS_KEY': settings.AWS_SECRET_ACCESS_KEY,
                        'AWS_REGION': settings.REGION_NAME,
                    }
                }
            )
        except Exception as e:
            logger.exception(e)

    def delete_lambda(self, function_name):
        """
        Deletes the specified lambda function.
        """
        try:
            lambda_client = self._get_client('lambda')
            lambda_client.delete_function(
                FunctionName=function_name
            )
            # remove the lambda function zip file
            os.remove(LAMBDA_ZIP)
        except Exception as e:
            logger.exception('Error while deleting lambda function')
            raise e

    def invoke_function(self, function_name):
        """
        Invokes the specified function and returns the result.
        """
        try:
            lambda_client = self._get_client('lambda')
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event'
            )
            logger.info(response)
        except Exception as e:
            logger.exception('Error while invoking function')
            raise e


class StatisticService:
    @staticmethod
    def get_statistics(user_uuid):
        return LocalstackDynamoDB().query(user_uuid)
