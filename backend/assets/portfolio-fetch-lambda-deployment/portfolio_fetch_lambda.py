from user_portfolios_dao import UserPortfoliosDAO

import json
import requests

user_portfolio_dao = UserPortfoliosDAO()


def handler(event, context):
    print(f'event: {event}')

    username = event['pathParameters']['user']

    try:
        response = user_portfolio_dao.get_user_portfolio(username)

        if 'Item' not in response:
            user_portfolio_dao.create_new_user_portfolio(username)
            response = user_portfolio_dao.get_user_portfolio(username)

        portfolio = []

        for item in response['Item']['stocks']['L']:
            stock_id = item['M']['stock-id']['S']
            held = item['M']['held']['N']
            res = requests.get(f'http://54.224.164.41:8000/Stock_{stock_id}').json()
            stock_price = str(float(json.loads(res['data'])['p']))
            stock_value = str(float(int(held) * float(stock_price)))
            stock_short_name = item['M']['short-name']['S']

            if int(held) == 0:
                continue

            portfolio.append({
                'stock-price': stock_price,
                'quantity': held,
                'stock-id': stock_id,
                'stock-short-name': stock_short_name,
                'stock-value': stock_value
            })

        print(portfolio)

        formatted_response = {
            'cash': response['Item']['cash'],
            'portfolio': portfolio
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
                'message': formatted_response
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

