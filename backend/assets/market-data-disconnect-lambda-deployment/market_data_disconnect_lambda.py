import boto3

dynamodb_client = boto3.client('dynamodb')


def handler(event, context):
    print(event)
    connection_id = event['requestContext']['connectionId']

    try:
        response = dynamodb_client.delete_item(
            TableName='market-data-connections',
            Item={
                'connection-id': {
                    'S': connection_id
                }
            }
        )
        print(response)

    except Exception as e:
        print(f'Error: {e}')
