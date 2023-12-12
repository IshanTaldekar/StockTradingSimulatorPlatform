import boto3

NEW_USER_STARTER_AMOUNT = 10000


class UserPortfoliosDAO:
    def __init__(self):
        self.dynamodb_client = boto3.client('dynamodb')
        self.table_name = 'user-portfolios'

    def get_user_portfolio(self, username):
        print(f'[UserPortfolioDAO] fetching user portfolio for {username}')
        return self.dynamodb_client.get_item(
            TableName=self.table_name,
            Key={
                'username': {
                    'S': username
                }
            }
        )

    def update_user_portfolio(self, new_item):
        print(f'[UserPortfolioDAO] updating user portfolio for {new_item["username"]["S"]}')

        update_expression = 'SET '
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in new_item.items():
            if key != 'username':
                placeholder = f':{key}'
                update_expression += f'#{key} = {placeholder}, '
                expression_attribute_values[placeholder] = value
                expression_attribute_names[f'#{key}'] = key

        update_expression = update_expression.rstrip(', ')

        print(f'[UserPortfolioDAO] update expression: {update_expression}')
        print(f'[UserPortfolioDAO] expression attribute values: {expression_attribute_values}')
        print(f'[UserPortfolioDAO] expression attribute names: {expression_attribute_names}')

        return self.dynamodb_client.update_item(
            TableName=self.table_name,
            Key={
                'username': {
                    'S': new_item['username']['S']
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues='UPDATED_NEW'
        )

    def create_new_user_portfolio(self, username):
        print(f'[UserPortfolioDAO] creating user portfolio for {username}')

        new_portfolio_entry = {
            'username': {
                'S': username
            },
            'cash': {
                'N': str(NEW_USER_STARTER_AMOUNT)
            },
            'stocks': {
                'L': []
            }
        }

        return self.dynamodb_client.put_item(
            TableName=self.table_name,
            Item=new_portfolio_entry
        )

