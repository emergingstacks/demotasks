import requests
import logging
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime, timedelta

current_time_epoch = datetime.now().timestamp()
last_thirty_mins_epoch = (datetime.now() - timedelta(hours=0, seconds=15)).timestamp()

url = "http://localhost/loki/api/v1/query_range?start={}&end={}".format(last_thirty_mins_epoch, current_time_epoch)
# data = 'query={job="nginx-ingress/nginx-ingress", release="nginx-ingress-bidder"} | pattern `<remote_addr> ' \
#        '<remote_user> <_> <time_local> "<method> <request_uri> <protocol>" <status> <body_bytes_sent> ' \
#        '"<http_referer>" "<http_user_agent>" <request_length> <request_time> <proxy_upstream_name> <upstream_addr> ' \
#        '<upstream_response_length> <upstream_response_time> <upstream_status> <request_id>` '

data = 'query={job="nginx-ingress/nginx-ingress", release="nginx-ingress-bidder"} | pattern `<remote_addr> ' \
       '<remote_user> <_> <time_local> "<method> <request_uri> <protocol>" <status> <body_bytes_sent> ' \
       '"<http_referer>" "<http_user_agent>" <request_length> <request_time> <proxy_upstream_name> ' \
       '<proxy_alternative_upstream_name> <upstream_addr> ' \
       '<upstream_response_length> <upstream_response_time> <upstream_status> <request_id>` '

response = requests.post(url=url, params=data).json()
proxy_upstream_list = []
for i in response['data']['result']:
    proxy_upstream_name = str(i['stream']['proxy_upstream_name']).strip("[]")
    if not proxy_upstream_name in proxy_upstream_list:
        proxy_upstream_list.append(proxy_upstream_name)

list1 = []
list2 = []


def dump_to_json(file_name, proxy_list):
    with open(file=file_name, mode='a+') as write_stream:
        for item in proxy_list:
            write_stream.write("%s\n" % proxy_list)


# def upload_to_s3(filename, proxy_list):
#     s3 = boto3.client('s3')
#     bucket_name = ''


for proxy_list in proxy_upstream_list:
    for i in response['data']['result']:
        if str(i['stream']['proxy_upstream_name']).strip("[]") == proxy_list:
            list1.append(i['stream'])
    list2.append({
        proxy_list: list1
    })

    filename = "{}-{}.log".format(proxy_list, current_time_epoch)
    dump_to_json(filename, list2)
    # upload_to_s3(filename, proxy_list)
    list2.clear()
    list1.clear()
