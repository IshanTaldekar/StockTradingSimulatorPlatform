import boto3
import time

dynamodb_client = boto3.client('dynamodb')


def handle_new_user_transaction(username, transaction_amount, stock_id, quantity, stock_price, timestamp):
    stocks_list = []
    transaction_success = True

    if transaction_amount < 10000:
        amount = 10000 - transaction_amount
        stocks_list.append(
            {
                'M': {
                    'stock-id': {
                        'S': stock_id
                    },
                    'transactions': {
                        'L': [
                            {
                                'quantity': {
                                    'N': quantity
                                },
                                'amount': {
                                    'N': str(transaction_amount)
                                },
                                'buy-price': {
                                    'N': str(stock_price)
                                },
                                'buy-timestamp': {
                                    'S': timestamp
                                }
                            }
                        ]
                    }
                }
            }
        )
    else:
        amount = 10000
        transaction_success = False

    response = dynamodb_client.put_item(
        TableName='user-portfolios',
        Item={
            'username': {
                'S': username
            },
            'cash': {
                'N': str(amount)
            },
            'stocks': {
                'L': stocks_list
            }
        }
    )

    if transaction_success:
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
    else:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
            },
            'message': 'Operation failed: insufficient funds'
        }


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
            return handle_new_user_transaction(
                username,
                transaction_amount,
                stock_id,
                quantity,
                stock_price,
                timestamp
            )

        if transaction_amount > int(response['Item']['cash']):
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
                },
                'message': 'Operation failed: insufficient funds'
            }

        new_transaction = {
            'quantity': {
                'N': quantity
            },
            'amount': {
                'N': str(transaction_amount)
            },
            'buy-price': {
                'N': str(stock_price)
            },
            'buy-timestamp': {
                'S': timestamp
            }
        }

        transaction_inserted = False

        for item in response['Item']['stocks']:
            if item['stock-id'] == stock_id:
                item['transactions'].append(new_transaction)
                transaction_inserted = True

        if not transaction_inserted:
            response['Item']['stocks'].append(
                {
                    'M': {
                        'stock-id': {
                            'S': stock_id
                        },
                        'transactions': {
                            'L': [new_transaction]
                        }
                    }
                }
            )

        update_expression = 'SET '
        expression_attribute_values = {}
        expression_attribute_names = {}

        item = response['Item']

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
                    'S': 'BUY'
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
