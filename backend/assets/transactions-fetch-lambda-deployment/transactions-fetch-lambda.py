import boto3
from boto3.dynamodb.conditions import Key
import json

dynamo_db = boto3.resource('dynamodb')
user_transactions_table = dynamo_db.Table('user-transactions')


def handler(event, context):
    print(f'event: {event}')

    username = event['pathParameters']['username']

    try:
        response = user_transactions_table.query(
            KeyConditionExpression=Key('username').eq(username),
            ScanIndexForward=False,
            Limit=20
        )
        print(f'response: {response}')

        items = response['Items']

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
            },
            'body': json.dumps(items)
        }
    except Exception as e:
        print(f'exception: {e}')

    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
        },
        'error': 'Failed to fetch transactions'
    }
