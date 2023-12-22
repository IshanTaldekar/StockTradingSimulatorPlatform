import boto3
import json
from eventregistry import *
from opensearchpy import OpenSearch, RequestsHttpConnection
from botocore.exceptions import ClientError

#secret_name = 'NewsSummaryMasterUserCA21B9-QkXben5lAXO2'
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

print(user)

username = user['username']
password = user['password']

print(username, password)

elasticsearch_endpoint = 'search-news-summary-adz52g6kcerbztcrc4v33ehclm.us-east-1.es.amazonaws.com'


elasticsearch_client = OpenSearch(
				hosts=[{'host':elasticsearch_endpoint ,'port': 443}], 
				http_auth=(username, password),
				use_ssl = True, 
				verify_certs=True
		)

# TODO: replace
index_name = 'tests'

def save_to_es(news_url, summary, id_news, title):
    print('Saving News to open Search')
    body = {
      'summary': summary,
      'key': id_news,
      'createdTimestamp': str(int(time.time())),
      'url': news_url,
      'title': title
      
    }
    ret = elasticsearch_client.index(index=index_name, id=id_news, body=body, refresh = True)
    print('Data saved:', ret)
    return

def sagemaker_inference(input_data):
    input_payload = {
        'inputs': input_data
    }

    
    response = sm_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=json.dumps(input_payload),  
        ContentType='application/json',  
    )
    result = json.loads(response['Body'].read().decode())
    
    return result["summary"]

er = EventRegistry(apiKey = "adf8be6c-1510-4383-807b-388821552ce8")
sm_runtime = boto3.client('sagemaker-runtime')
endpoint_name = 'huggingface-pytorch-inference'

usUri = er.getLocationUri("USA")   

def handler(event, context):
    q = QueryArticlesIter(
        keywords = QueryItems.OR(["Stock news"]),
        minSentiment = 0.4,
        sourceLocationUri = usUri,
        dataType = ["news", "blog"])


    for art in q.execQuery(er, sortBy = "date", maxItems = 50):
        title = art['title']
        news = art["body"]
        news_url = art["url"]
        id_news = art['uri']
        summary = sagemaker_inference(news)
        save_to_es(news_url, summary, id_news, title)


    return {
        'statusCode': 200,
        'body': json.dumps("News Updated")
    }
