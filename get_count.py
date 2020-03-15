#!/usr/bin/env python3

import requests
import json

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
        print(f"Cases increased from {curcount} to {newcount}.")

        s3 = boto3.client('s3')
        retval = s3.put_object(
            Bucket='tn-gov-covid-19',
            Key='count.txt',
            Body=str(newcount)
        )

def lambda_handler(event, context):
    json.dumps(event, indent=2, default=str)
    
    page = requests.get("https://www.tn.gov/health/cedep/ncov.html")

    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    
    count = int(list(list(soup.find_all('tbody')[0].children)[3].find_all('td'))[1].get_text())
    update_count(count)
    
if __name__ == '__main__':
    lambda_handler('', '')
    
