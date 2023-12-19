from multiprocessing import Process, Queue
import redis
from dotenv import load_dotenv
import os
import requests
from graphqlclient import GraphQLClient
import json
import requests

def fetch_current_forex_prices(q):
    r = redis.Redis(
        host='44.204.13.24',
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

def perform_mutations_appsync(api_key, q):
    while True:
        msg = q.get()
        print("got msg:", msg)
        url = 'https://n7ztzr43sna5vgigikzbrkbrmq.appsync-api.us-east-1.amazonaws.com/graphql'
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
    api_key = os.getenv("API_KEY_APPSYNC")
    p1 = Process(target=fetch_current_forex_prices, args=(q,))
    p2 = Process(target=perform_mutations_appsync, args=(api_key, q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
