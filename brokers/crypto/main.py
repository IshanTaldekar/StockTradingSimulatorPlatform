import websocket
from multiprocessing import Process, Queue
import redis
import boto3
import json
from dotenv import load_dotenv
import os
from pprint import pprint


def update_redis_cache(url, q):
    r = redis.Redis(
        host=url,
        port='6379',
        decode_responses=True
    )

    while True:
        msg = json.loads(q.get())
        if msg['type'] == "trade":
            data = msg['data'][-1]
            pair = "Crypto_" + data['s'].replace(':', "_")
            r.set(pair, json.dumps({
                'price': data['p'],
                't': data['t'],
                'v': data['v'],
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
            SecretId="finhub-token"
            )['SecretString']
        )['token']

    return api_key



def stream_crypto_prices(api_key, q):
    def on_message(ws, message):
        q.put(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')

    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={api_key}",
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close,
                            on_open = on_open)

    ws.run_forever()

if __name__ == '__main__':
    load_dotenv()
    q = Queue()
    api_key = get_api_key()
    redis_url = os.getenv("REDIS_URL")
    p1 = Process(target=stream_crypto_prices, args=(api_key, q,))
    p2 = Process(target=update_redis_cache, args=(redis_url, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
