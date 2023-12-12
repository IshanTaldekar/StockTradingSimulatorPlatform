import boto3


class UserTransactionsDAO:
    def __init__(self):
        self.dynamodb_client = boto3.client('dynamodb')
        self.table_name = 'user-transactions'

    def add_transaction(self, username, action, stock_id, quantity, stock_price, transaction_amount, timestamp,
                        timestamp_epoch):
        print(f'[UserTransactionsDAO] adding transaction for {username}')

        return self.dynamodb_client.put_item(
            TableName=self.table_name,
            Item={
                'username': {
                    'S': str(username)
                },
                'action': {
                    'S': str(action)
                },
                'stock-id': {
                    'S': str(stock_id)
                },
                'quantity': {
                    'N': str(quantity)
                },
                'stock-price': {
                    'N': str(stock_price)
                },
                'transaction-amount': {
                    'N': str(transaction_amount)
                },
                'timestamp': {
                    'S': str(timestamp)
                },
                'timestamp-epoch': {
                    'N': str(timestamp_epoch)
                }
            }
        )

