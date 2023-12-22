import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from botocore.exceptions import ClientError

secret_name = 'NewsSummaryMasterUserCA21B9-3S9eiHVsGh8K'
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
    user = json.loads(get_secret_value_response['SecretString'])
except ClientError as e:
    print(f'failed to fetch secret: {e}')
    raise e


username = user['username']
password = user['password']


elasticsearch_endpoint = 'search-news-summary-adz52g6kcerbztcrc4v33ehclm.us-east-1.es.amazonaws.com'


elasticsearch_client = OpenSearch(
				hosts=[{'host':elasticsearch_endpoint ,'port': 443}], 
				http_auth=(username, password),
				use_ssl = True, 
				verify_certs=True
		)


index_name = 'tests'


def handler(event, context):

    query = {
        'size': 10,
        'query': {
            'match_all': {}
        },
        "sort": [
            {"createdTimestamp.keyword": {"order": "desc"}}
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
        'body': json.dumps(response['hits']['hits'])
    }
