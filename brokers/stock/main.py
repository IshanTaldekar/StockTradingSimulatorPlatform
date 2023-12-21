from multiprocessing import Process, Queue
import redis
import json
from dotenv import load_dotenv
import os
from pprint import pprint
import requests
import time
import boto3

STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "F", "TSLA", "NVDA", "NFLX", "INTC", "AMD"]

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


def update_redis_cache(url, q):
    r = redis.Redis(
        host=url,
        port='6379',
        decode_responses=True
    )

    while True:
        msg = q.get()
        pair = "Stock_" + msg['symbol']
        r.set(pair, json.dumps({
            'shortName': msg['shortName'],
            'p': msg['regularMarketPrice']['raw'],
            't': int(time.time() * 1000)
        }))
        print("Updated pair:", pair)
    


def stream_stocks_prices(q):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
    while True:
        for stock in STOCKS:
            res = requests.get(f"https://query1.finance.yahoo.com/v1/finance/lookup?query={stock}&type=equity", headers=headers)
            if res.status_code != 200:
                continue
            payload = res.json()
            for r in payload['finance']['result']:
                for d in r['documents']:
                    if d['symbol'] == stock:
                        q.put(d)
        time.sleep(5)

if __name__ == '__main__':
    load_dotenv()
    q = Queue()
    redis_url = get_from_secrets('redis-server', 'ip')
    p1 = Process(target=stream_stocks_prices, args=(q,))
    p2 = Process(target=update_redis_cache, args=(redis_url, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

