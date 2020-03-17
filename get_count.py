#!/usr/bin/env python3

import json
import os
import requests

import boto3
# from botocore.errorfactory import NoSuchKey
import botocore.exceptions
from bs4 import BeautifulSoup

def get_s3_count():
    s3 = boto3.client('s3')
    try:
        retval = s3.get_object(
            Bucket='tn-gov-covid-19',
            Key='count.txt')
        retval = retval['Body'].read()
    except botocore.exceptions.ClientError as e:
        if type(e).__name__ == 'NoSuchKey':
            retval = '0'
        else:
            raise e
    return int(retval)
    
def update_count(newcount):
    curcount = get_s3_count()
    if newcount > curcount:

        s3 = boto3.client('s3')
        retval = s3.put_object(
            Bucket='tn-gov-covid-19',
            Key='count.txt',
            Body=str(newcount)
        )
    return (curcount, newcount)

def lambda_handler(event, context):
    json.dumps(event, indent=2, default=str)
    
    page = requests.get("https://www.tn.gov/health/cedep/ncov.html")

    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    
    count = int(list(list(soup.find_all('tbody')[0].children)[3].find_all('td'))[1].get_text())
    (curcount, newcount) = update_count(count)
    if curcount < newcount:
        sns = boto3.client('sns')
        topic_arn = os.environ['SnsTopicArn'] # Will except if not there
        message = {
            'default': f"TN cases increased from {curcount} to {newcount}.",
            'sms': f"TN cases increased from {curcount} to {newcount}.",
            'email': f"TN cases increased from {curcount} to {newcount}."
        }
        sns.publish(
            TargetArn=topic_arn,
            Message=json.dumps(message, default=str),
            MessageStructure='json'
        )
        
    
if __name__ == '__main__':
    lambda_handler('', '')
    
