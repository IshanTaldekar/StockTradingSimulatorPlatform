from multiprocessing import Process, Queue
import redis
import boto3
import json
from polygon import WebSocketClient
from polygon.websocket.models import Market
from dotenv import load_dotenv
import os

def update_redis_cache(q):
    r = redis.Redis(
        host='44.204.13.24',
        port='6379',
        decode_responses=True
    )

    while True:
        msg = q.get()
        if msg.event_type == "CAS":
            pair = "Forex_" + msg.pair.replace('/', "_")
            r.set(pair, json.dumps({
                'open': msg.open,
                'close': msg.close,
                'high': msg.high,
                'low': msg.low,
                'st': msg.start_timestamp,
                'et': msg.end_timestamp,
            }))
            print("Updated pair:", pair)


def get_api_key():
    session = boto3.session.Session()
    sm = session.client(
        service_name = 'secretsmanager',
        region_name = 'us-east-1',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    api_key = json.loads(
        sm.get_secret_value(
            SecretId="polygon-api-key"
            )['SecretString']
        )['api-key']

    return api_key



def stream_forex_prices(api_key, q):
    client = WebSocketClient(market=Market.Forex, api_key=api_key, verbose=True)
    client.subscribe("CAS.*")

    def handle_msg(msgs):
        for msg in msgs:
            q.put(msg)

    client.run(handle_msg)


if __name__ == '__main__':
    load_dotenv()
    q = Queue()
    api_key = get_api_key()
    p1 = Process(target=stream_forex_prices, args=(api_key, q,))
    p2 = Process(target=update_redis_cache, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    