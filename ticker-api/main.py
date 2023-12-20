from flask import Flask, jsonify
import os
import redis
from http import HTTPStatus

app = Flask(__name__)

r = redis.Redis(
        host=os.getenv("REDIS_URL"),
        port='6379',
        decode_responses=True
    )

@app.route("/", defaults={'ticker': None})
@app.route("/<ticker>")
def hello_world(ticker):
    if ticker is None:
        return jsonify(
                message="provide the ticker name as parameter",    
            ), HTTPStatus.BAD_REQUEST
    res = r.get(ticker)
    if res is None:
        return jsonify(
                message="ticker doesn't exist in the redis store",    
            ), HTTPStatus.NOT_FOUND
    return jsonify(
            name=ticker,
            data=res
        ), HTTPStatus.OK

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)

