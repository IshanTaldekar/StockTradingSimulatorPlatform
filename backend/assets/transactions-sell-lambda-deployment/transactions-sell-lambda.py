import boto3
import time

dynamodb_client = boto3.client('dynamodb')


def handler(event, context):
    print(f'event: {event}')

    username = event['body']['username']
    stock_id = event['body']['stockId']
    quantity = event['body']['quantity']

    timestamp = time.time()

    # TODO: Add timestream integration to get latest stock price
    stock_price = -1

    try:
        response = dynamodb_client.get_item(
            TableName='user-portfolios',
            Key={
                'username': {
                    'S': username
                }
            }
        )

        transaction_amount = (int(quantity) * stock_price)

        if 'Item' not in response:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
                },
                'message': 'Operation failed'
            }

        transactions = []

        for item in response['Item']['stocks']:
            if item['stock-id'] == stock_id:
                transactions = item['transactions']
                break

        stocks_held = 0

        for transaction in transactions:
            stocks_held += transaction['quantity']

        if stocks_held < quantity:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
                },
                'message': 'Operation failed: insufficient stocks'
            }

        for transaction in transactions:
            if stocks_held == 0:
                break

            if stocks_held >= transaction['quantity']:
                stocks_held -= transaction['quantity']
                transaction['quantity'] = 0
            else:
                transaction['quantity'] -= stocks_held
                stocks_held = 0

        while transactions[0]['quantity'] == 0:
            transactions.pop(0)

        for item in response['Item']['stocks']:
            if item['stock-id'] == stock_id:
                item['transactions'] = transactions

        update_expression = 'SET '
        expression_attribute_values = {}
        expression_attribute_names = {}

        item = response['Item']
        item['cash'] = str(int(item['cash']) + transaction_amount)

        for key, value in item.items():
            if key != 'username':
                placeholder = f':{key}'
                update_expression += f'#{key} = {placeholder}, '
                expression_attribute_values[placeholder] = value
                expression_attribute_names[f'#{key}'] = key

        update_expression = update_expression.rsplit(', ')

        response = dynamodb_client.update_item(
            TableName='user-portfolios',
            Key={
                'username': {
                    'S': username
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues='UPDATED_NEW'
        )

        print(f'updated portofio entry: {response}')

        response = dynamodb_client.put_item(
            TableName='user-transactions',
            Item={
                'username': {
                    'S': username
                },
                'action': {
                    'S': 'SELL'
                },
                'stock-id': {
                    'S': stock_id
                },
                'quantity': {
                    'N': quantity
                },
                'stock-price': {
                    'N': str(stock_price)
                },
                'transaction-amount': {
                    'N': str(transaction_amount)
                }
            }
        )

    except Exception as e:
        print(f'Error: {e}')

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
            },
            'message': f'Operation failed: {e}'
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
        },
        'message': 'Operation successful'
    }
