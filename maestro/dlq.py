import boto3
import sys
import os
import json
from botocore.exceptions import ClientError

sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')
sqs = boto3.resource('sqs')

def get_sns_arn(topic_name):
  list_of_topics = []
  try:
    existing_topics = sns_client.list_topics()
    dumper = json.dumps(existing_topics, indent=4)
    loader = json.loads(dumper)
    topics = loader['Topics']

    for obj in topics:
      for key, value in obj.items():
        list_of_topics.append(value)

    for item in list_of_topics:
      if topic_name in item:
        return item

  except ClientError as error:
    print(json.dumps(error.response, indent=4))

def get_sqs_arn(sqs_name):
  try:
    get_queues = sqs_client.list_queues(
                  QueueNamePrefix=sqs_name
                )

    dump = json.dumps(get_queues, indent=4)
    loads = json.loads(dump)

    if loads['ResponseMetadata']['HTTPStatusCode'] == 200:
      queue_urls = loads['QueueUrls'][0]
      if len(queue_urls)>0:
        queue = sqs.Queue(queue_urls)
        return queue.attributes['QueueArn']

  except ClientError as error:
    print(error.response['Error']['Message'])
