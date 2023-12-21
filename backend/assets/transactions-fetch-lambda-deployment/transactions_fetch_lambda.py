import boto3
from boto3.dynamodb.conditions import Key
import json

dynamodb_client = boto3.client('dynamodb')


def handler(event, context):
    print(f'event: {event}')

    username = event['pathParameters']['username']

    try:
        response = dynamodb_client.query(
            TableName='user-transactions',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={
                ':username': {'S': username}
            },
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
            'body': json.dumps({
                'message': 'Operation failed'
            })
        }
