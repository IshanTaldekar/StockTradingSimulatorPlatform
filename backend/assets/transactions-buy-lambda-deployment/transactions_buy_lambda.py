from user_portfolios_dao import UserPortfoliosDAO
from user_transactions_dao import UserTransactionsDAO
import requests

import json
from datetime import datetime, timezone

user_portfolio_dao = UserPortfoliosDAO()
user_transactions_dao = UserTransactionsDAO()


def handler(event, context):
    print(f'event: {event}')

    body = json.loads(event['body'])

    username = body['username']
    stock_id = body['stockId']
    quantity = body['quantity']

    utc_timestamp = datetime.now(timezone.utc)
    formatted_utc_timestamp = utc_timestamp.strftime('%m/%d/%Y %H:%M:%S')

    res = requests.get(f'http://54.224.164.41:8000/Stock_{stock_id}').json()
    stock_price = float(json.loads(res['data'])['p'])
    short_name = json.loads(res['data'])['shortName']

    print(f'stock price: {stock_price}')
    print(f'stock name: {short_name}')

    transaction_amount = int(quantity) * stock_price

    try:
        user_portfolio_response = user_portfolio_dao.get_user_portfolio(username)

        if 'Item' not in user_portfolio_response:
            user_portfolio_dao.create_new_user_portfolio(username)
            user_portfolio_response = user_portfolio_dao.get_user_portfolio(username)

        if transaction_amount > float(user_portfolio_response['Item']['cash']['N']):
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
                    'message': 'Operation failed: insufficient funds'
                })
            }

        new_transaction = {
            'M': {
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
                    'S': formatted_utc_timestamp
                }
            }
        }

        transaction_inserted = False

        for item in user_portfolio_response['Item']['stocks']['L']:
            if item['M']['stock-id']['S'] == stock_id:
                item['M']['held']['N'] = str(int(item['M']['held']['N']) + int(quantity))
                item['M']['transactions']['L'].append(new_transaction)
                transaction_inserted = True
                break

        if not transaction_inserted:
            user_portfolio_response['Item']['stocks']['L'].append(
                {
                    'M': {
                        'stock-id': {
                            'S': stock_id
                        },
                        'short-name': {
                            'S': short_name
                        },
                        'held': {
                            'N': quantity
                        },
                        'transactions': {
                            'L': [new_transaction]
                        }
                    }
                }
            )

        user_portfolio_response['Item']['cash']['N'] = str(float(user_portfolio_response['Item']['cash']['N']) -
                                                           transaction_amount)
        user_portfolio_dao.update_user_portfolio(user_portfolio_response['Item'])

        user_transactions_dao.add_transaction(
            username,
            'BUY',
            stock_id,
            quantity,
            stock_price,
            transaction_amount,
            formatted_utc_timestamp,
            utc_timestamp.timestamp()
        )

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
                'message': 'Operation successful'
            })
        }

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
            'body': json.dumps({
                'message': f'Operation failed: {e}'
            })
        }
