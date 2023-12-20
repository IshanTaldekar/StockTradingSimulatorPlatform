from multiprocessing import Process, Queue
import redis
import json
from dotenv import load_dotenv
import os
from pprint import pprint
import requests
import time

STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "F", "TSLA", "NVDA", "NFLX", "INTC", "AMD"]

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
    redis_url = os.getenv("REDIS_URL")
    p1 = Process(target=stream_stocks_prices, args=(q,))
    p2 = Process(target=update_redis_cache, args=(redis_url, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
