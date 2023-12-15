import boto3
import json
from elasticsearch import Elasticsearch
from botocore.exceptions import ClientError

secret_name = 'NewsSummaryMasterUserCA21B9-QkXben5lAXO2'
region_name = 'us-east-1'

session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    print(f'failed to fetch secret: {e}')
    raise e

print(get_secret_value_response)

username = get_secret_value_response['username']
password = get_secret_value_response['password']

elasticsearch_endpoint = 'search-news-summary-77kckz65rityx5xplsi5x72ss4.us-east-1.es.amazonaws.com'

elasticsearch_client = Elasticsearch(
    hosts=[{'host': elasticsearch_endpoint, 'port': 443}],
    http_auth=(username, password),
    use_ssl=True,
    verify_certs=True
)

# TODO: replace
index_name = 'index'


def handler(event, context):
    query = {
        'size': 10,
        'query': {
            'match_all': {}
        },
        'sort': [
            {'timestamp': {'order': 'desc'}}
        ]
    }

    response = elasticsearch_client.search(index=index_name, body=query)
    print(response)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
        },
        'message': json.dumps(response['hits']['hits'])
    }
