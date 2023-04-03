from services import LocalstackDynamoDB


def handler(event, context):
    LocalstackDynamoDB().put_item(event)
