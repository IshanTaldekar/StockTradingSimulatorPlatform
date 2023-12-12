import json
from eventregistry import *
import boto3
import logging
import urllib
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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


def save_to_es(news_url, summary, id_news):
    print('Saving News to open Search')
    body = {
      'summary': summary,
      'key': id_news,
      'createdTimestamp': str(int(time.time())),
      'url': news_url,
      
    }
    ret = os.index(index="tests", id=id_news, body=body, refresh = True)
    print('NLPA -- ES Push response:', ret)
    return

os = OpenSearch(
				hosts=[{'host': 'search-news-summary-77kckz65rityx5xplsi5x72ss4.us-east-1.es.amazonaws.com','port': 443}], 
				http_auth=('master', 'PC=0#8rvAn.g6S;Vj,gZ70VLS~qNBqx8'), 
				use_ssl = True, 
				verify_certs=True, 
				connection_class=RequestsHttpConnection
		)

er = EventRegistry(apiKey = "adf8be6c-1510-4383-807b-388821552ce8")

sm_runtime = boto3.client('sagemaker-runtime')
endpoint_name = 'huggingface-pytorch-inference-2023-12-13-19-20-06-220'

usUri = er.getLocationUri("USA")   

q = QueryArticlesIter(
    keywords = QueryItems.OR(["Business News"]),
    minSentiment = 0.4,
    sourceLocationUri = usUri,
    dataType = ["news", "blog"])


for art in q.execQuery(er, sortBy = "date", maxItems = 5):
    news = art["body"]
    news_url = art["url"]
    id_news = art['uri']
    summary = sagemaker_inference(news)
    save_to_es(news_url, summary, id_news)
    print(summary)

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(summary)
    }
