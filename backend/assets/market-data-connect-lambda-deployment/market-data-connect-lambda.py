import boto3

dynamodb_client = boto3.client('dynamodb')


def handler(event, context):
    print(f'event: {event}')

    stock_id = event['queryStringParameters']['stock_id']
    connection_id = event['requestContext']['connectionId']

    # TODO: Get current values from timestream (latest 100 values)

    try:
        response = dynamodb_client.get_item(
            TableName='market-data-connections',
            Key={
                'connection-id': {
                    'S': connection_id
                }
            }
        )

        if 'Item' not in response:
            response = dynamodb_client.put_item(
                TableName='market-data-connections',
                Item={
                    'connection-id': {
                        'S': connection_id
                    },
                    'stock_id': {
                        'S': stock_id
                    }
                }
            )
        else:
            response = dynamodb_client.update_item(
                TableName='market-data-connections',
                Item={
                    'connection-id': {
                        'S': connection_id
                    },
                    'stock_id': {
                        'S': stock_id
                    }
                }
            )

        print(f'response: {response}')

        # TODO: return last 100 values
    except Exception as e:
        print(f'Error: {e}')
