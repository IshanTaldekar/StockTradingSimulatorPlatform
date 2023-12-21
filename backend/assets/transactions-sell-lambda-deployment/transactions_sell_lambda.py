from user_portfolios_dao import UserPortfoliosDAO
from user_transactions_dao import UserTransactionsDAO

import boto3
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

    # TODO: Add timestream integration to get latest stock price
    stock_price = -1
    transaction_amount = int(quantity) * stock_price

    try:
        user_portfolio_response = user_portfolio_dao.get_user_portfolio(username)

        if 'Item' not in user_portfolio_response:
            user_portfolio_dao.create_new_user_portfolio(username)
            user_portfolio_response = user_portfolio_dao.get_user_portfolio(username)

        transactions = []

        for item in user_portfolio_response['Item']['stocks']['L']:
            if item['M']['stock-id']['S'] == stock_id:
                transactions = item['M']['transactions']['L']
                break

        stocks_held = 0

        for transaction in transactions:
            stocks_held += int(transaction['M']['quantity']['N'])

        if stocks_held < int(quantity):
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
                    'message': 'Operation failed: insufficient stocks held'
                })
            }

        for transaction in transactions:
            if stocks_held == 0:
                break

            if stocks_held >= int(transaction['M']['quantity']['N']):
                stocks_held -= int(transaction['M']['quantity']['N'])
                transaction['M']['quantity']['N'] = '0'
            else:
                transaction['M']['quantity']['N'] = str(int(transaction['M']['quantity']['N']) - stocks_held)
                stocks_held = 0

        while len(transactions) != 0 and transactions[0]['M']['quantity']['N'] == '0':
            transactions.pop(0)

        for item in user_portfolio_response['Item']['stocks']['L']:
            if item['M']['stock-id']['S'] == stock_id:
                item['M']['transactions']['L'] = transactions

        item = user_portfolio_response['Item']
        item['cash']['N'] = str(int(item['cash']['N']) + transaction_amount)

        user_portfolio_dao.update_user_portfolio(user_portfolio_response['Item'])

        user_transactions_dao.add_transaction(
            username,
            'SELL',
            stock_id,
            quantity,
            stock_price,
            transaction_amount,
            formatted_utc_timestamp,
            utc_timestamp.timestamp()
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
            'body': json.dumps({
                'message': f'Operation failed: {e}'
            })
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
        'body': json.dumps({
            'message': 'Operation successful'
        })
    }
