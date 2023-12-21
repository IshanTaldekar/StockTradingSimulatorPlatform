from multiprocessing import Process, Queue
import redis
from dotenv import load_dotenv
import os
import requests
import json
import requests
import boto3
from botocore.exceptions import ClientError

def get_from_secrets(SecretId, key):
    session = boto3.session.Session()
    sm = session.client(
        service_name = 'secretsmanager',
        region_name = 'us-east-1',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    value = json.loads(
        sm.get_secret_value(
            SecretId=SecretId
            )['SecretString']
        )[key]

    return value

def fetch_current_forex_prices(url, q):
    r = redis.Redis(
        host=url,
        port='6379',
        decode_responses=True
    )

    mobile = r.pubsub()

    mobile.psubscribe('__key*__:*')

    for msg in mobile.listen():
        name = msg['data']
        val = r.get(name)
        if val is not None:
            q.put({'name': name,'data': val})

def create_ts_client():
    session = boto3.session.Session()
    client = session.client(
        service_name = 'timestream-write',
        region_name = 'us-east-1',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    return client

def format_ticker_data_ts(ttype, name, data):
    if ttype == "Crypto":
        return [{
            'Dimensions': [
                {
                    'Name': 'crypto',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'price',
            'MeasureValue': str(data['price']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['t']),
            'TimeUnit': 'MILLISECONDS'
        }]
    elif ttype == "Forex":
        return [{
            'Dimensions': [
                {
                    'Name': 'currency',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'open',
            'MeasureValue': str(data['open']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['et']),
            'TimeUnit': 'MILLISECONDS'
        },
        {
            'Dimensions': [
                {
                    'Name': 'currency',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'close',
            'MeasureValue': str(data['close']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['et']),
            'TimeUnit': 'MILLISECONDS'
        }, 
        {
            'Dimensions': [
                {
                    'Name': 'currency',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'high',
            'MeasureValue': str(data['high']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['et']),
            'TimeUnit': 'MILLISECONDS'
        },
        {
            'Dimensions': [
                {
                    'Name': 'currency',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'low',
            'MeasureValue': str(data['low']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['et']),
            'TimeUnit': 'MILLISECONDS'
        }]
    elif ttype == "Stock":
        return [{
            'Dimensions': [
                {
                    'Name': 'stock',
                    'Value': name,
                    'DimensionValueType': 'VARCHAR'
                },
            ],
            'MeasureName': 'price',
            'MeasureValue': str(data['p']),
            'MeasureValueType': 'DOUBLE',
            'Time': str(data['t']),
            'TimeUnit': 'MILLISECONDS'
        }]

def perform_timestream_inserts(client, q):
    while True:
        msg = q.get()
        database_name = msg['name'].split('_')[0]
        table_name =  msg['name'].replace(f'{database_name}_', '')
        if len(table_name) < 3:
            table_name += "__"
        records = format_ticker_data_ts(database_name, table_name, json.loads(msg['data']))
        try:
            res = client.write_records(
                DatabaseName = database_name,
                TableName = table_name,
                Records=records
            )
            print('Inserted new record in', database_name, 'database and', table_name, 'table')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Created table", table_name, "in database", database_name)
                client.create_table(DatabaseName=database_name, TableName=table_name)

if __name__ == '__main__':
    load_dotenv()
    q = Queue()
    redis_url = get_from_secrets('redis-server', 'ip')
    ts_client = create_ts_client()
    p1 = Process(target=fetch_current_forex_prices, args=(redis_url, q,))
    p2 = Process(target=perform_timestream_inserts, args=(ts_client, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()



