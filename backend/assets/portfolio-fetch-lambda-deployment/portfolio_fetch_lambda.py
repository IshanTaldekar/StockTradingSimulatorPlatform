import boto3
import json

dynamodb_client = boto3.client('dynamodb')


def handler(event, context):
    print(f'event: {event}')

    username = event['pathParameters']['user']

    try:
        response = dynamodb_client.get_item(
            TableName='user-portfolios',
            Key={
                'username': {
                    'S': username
                }
            }
        )
        print(f'response: {response}')

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
            },
            'body': json.dumps({
                'message': response['Item']
            })
        }
    except Exception as e:
        print(f'error: {e}')

    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
        },
        'body': json.dumps({
            'message': 'Operation failed'
        })
    }

