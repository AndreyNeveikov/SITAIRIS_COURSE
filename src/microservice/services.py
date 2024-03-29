import logging
import os

import boto3
import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from fastapi import HTTPException

import settings

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')
LAMBDA_ZIP = 'lambda/lambda.zip'


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
                                       'WriteCapacityUnits': 10}
            )
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
        logger.info('-----CREATE LAMBDA FUNCTION-----')
        try:
            lambda_client = self._get_client('lambda')
            logger.info('-----GET LAMBDA CLIENT-----')
            with open(LAMBDA_ZIP, 'rb') as f:
                zipped_code = f.read()
            logger.info('-----TRY TO CREATE FUNCTION-----')
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',
                Role='arn:aws:iam::000000000000:role/lambda-role',
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

    def invoke_function(self, function_name, payload: bytes):
        """
        Invokes the specified function and returns the result.
        """
        try:
            lambda_client = self._get_client('lambda')
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',
                Payload=payload
            )
            logger.info(response)
        except Exception as e:
            logger.exception('Error while invoking function')
            raise e


class StatisticService:
    @staticmethod
    def get_statistics(user_uuid):
        return LocalstackDynamoDB().query(user_uuid)


class BaseTokenService:
    def __init__(self, request):
        self.token = request.headers.get('authorization', None)
        self.__payload = None

    def is_valid(self):
        if not (self.token and
                self.token.startswith(settings.AUTH_HEADER_PREFIX)):
            raise HTTPException(status_code=401, detail='Token is not valid')

        try:
            self.__payload = jwt.decode(
                jwt=self.token.replace(settings.AUTH_HEADER_PREFIX, ''),
                key=settings.ACCESS_TOKEN_KEY,
                algorithms=settings.JWT_ALGORITHM
            )
            return True

        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail=str(e))

        except (jwt.InvalidTokenError, jwt.DecodeError) as e:
            raise HTTPException(status_code=401, detail=str(e))

    def get_user_uuid_from_payload(self):
        uuid = self.__payload.get('user_uuid')
        return uuid
