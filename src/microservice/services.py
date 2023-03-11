import logging

import boto3
from botocore.exceptions import ClientError

import settings

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


class StatisticsRepository:
    def __init__(self):
        self.table = self.get_table()

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

    def __get_client(self, client_name):
        credentials = self.__get_credentials()
        client = boto3.client(service_name=client_name,
                              **credentials)
        return client

    def __get_resource(self, resource_name):
        credentials = self.__get_credentials()
        resource = boto3.resource(service_name=resource_name,
                                  **credentials)
        return resource

    def get_table(self):
        resource = self.__get_resource('dynamodb')
        client = self.__get_client('dynamodb')

        try:
            logger.info('Trying to create table...')
            table = resource.create_table(
                TableName=settings.DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'page_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'page_id', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10,
                                       'WriteCapacityUnits': 10})
            logger.info('Table successfully created.')
        except client.exceptions.ResourceInUseException:
            logger.info('Table has already exists.')
            table = resource.Table(settings.DYNAMODB_TABLE_NAME)
            logger.info('Get table by name.')
        return table

    def put_item(self, page: dict):
        response = self.table.put_item(Item=page)
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


class StatisticService:
    @staticmethod
    def get_statistics(page_id):
        return StatisticsRepository().get_item(page_id)

    @staticmethod
    def create_statistics(page_model):
        return StatisticsRepository.put_item(page_model)


