from multiprocessing import Process, Queue
import redis
from dotenv import load_dotenv
import os
import requests
import json
import requests
import boto3

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

def perform_mutations_appsync(api_key, url, q):
    while True:
        msg = q.get()
        print("got msg:", msg)
        headers = {
            'x-api-key': api_key
        }
        query = '''
            mutation PublishData {{
                publish(data: {}, name: "{}") {{
                    data
                    name
                }}
            }}
        '''.format(json.dumps(msg['data']), str(msg['name']))
        res = requests.post(url, json={'query': query, 'variables': {}, "operationName": "PublishData"}, headers=headers)
        if res.status_code == 200:
            print("send mutation to appsync")
            print(res.json())
        else:
            print("mutation cannot be performed")


if __name__ == '__main__':
    load_dotenv()
    q = Queue()
    api_key = get_from_secrets('appsync-details', 'key')
    redis_url = get_from_secrets('redis-server', 'ip')
    appsync_url = get_from_secrets('appsync-details', 'url')
    p1 = Process(target=fetch_current_forex_prices, args=(redis_url, q,))
    p2 = Process(target=perform_mutations_appsync, args=(api_key, appsync_url, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


