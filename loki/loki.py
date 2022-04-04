import json
import requests
import boto3
from datetime import datetime, timedelta
import logging
import os
import traceback

# Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
temp_list1 = []
temp_list2 = []
proxy_upstream_list = []

with open('config.json', mode='r+') as config_stream:
    logging.info("Reading config file")
    config = json.load(config_stream)

healthcheck_url = "{}/metrics".format(config['loki_base_url'])
try:
    logging.info("Checking if loki API endpoint is healthy")
    healthcheck = requests.get(url=healthcheck_url, timeout=10)
    logging.info("Loki API endpoint is healthy")
except:
    logging.error("Loki APi Endpoint is not responding")
    exit(1)

logging.info("Initializing s3 client")
s3 = boto3.client('s3')
bucket_name = config['bucket']

# Get current time in epoch
now = datetime.now()
current_time_epoch = datetime.now().timestamp()
last_epoch = (datetime.now() - timedelta(minutes=int(config['interval_in_minutes']))).timestamp()
# print(datetime.now())
# print(datetime.now() - timedelta(minutes=30))
url = "{}/loki/api/v1/query_range?limit=5000&start={}&end={}".format(str(config['loki_base_url']),
                                                                     last_epoch,
                                                                     current_time_epoch)
data = 'query={job="nginx-ingress/nginx-ingress", release="nginx-ingress-bidder"} | pattern `<remote_addr> ' \
       '<remote_user> <_> <time_local> "<method> <request_uri> <protocol>" <status> <body_bytes_sent> ' \
       '"<http_referer>" "<http_user_agent>" <request_length> <request_time> <proxy_upstream_name> ' \
       '<proxy_alternative_upstream_name> <upstream_addr> ' \
       '<upstream_response_length> <upstream_response_time> <upstream_status> <request_id>` '


# Write logs to json file
def dump_to_json(file_name, proxy_list):
    try:
        with open(file=file_name, mode='a+') as write_stream:
            for k in proxy_list:
                write_stream.write("%s\n" % json.dumps(k, indent=4))
    except:
        logging.error("Unable to write data to json")


# Upload log files to s3
def upload_to_s3(file_name, proxy_list_item, today):
    try:
        logging.info("Access using s3://{}/{}/{}/{}/{}/{}/{}".format(bucket_name,
                                                                     "ingress_logs",
                                                                     today.year,
                                                                     today.month,
                                                                     today.day,
                                                                     proxy_list_item,
                                                                     file_name))
        logging.info("Uploading {} to s3 bucket {}".format(file_name, bucket_name))
        s3.upload_file(file_name, bucket_name, "{}/{}/{}/{}/{}/{}".format("ingress_logs",
                                                                          today.year,
                                                                          today.month,
                                                                          today.day,
                                                                          proxy_list_item,
                                                                          file_name))
        os.remove(file_name)
    except:
        traceback.print_exc()
        logging.error("Unable to upload log files to S3, Check your network.")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


try:
    logging.info("Fetching logs from ingress controllers. This may take a while..")
    response = requests.post(url=url, params=data, timeout=30).json()
    logging.info("Creating a temporary list to store proxy_upstream_name")
    # proxy_upstream_list creation
    for data_stream in response['data']['result']:
        proxy_upstream_name = str(data_stream['stream']['proxy_upstream_name']).strip("[]")
        if not proxy_upstream_name in proxy_upstream_list:
            proxy_upstream_list.append(proxy_upstream_name)
    logging.info(str(proxy_upstream_list))
except:
    logging.error("Loki api is unresponsive")
    traceback.print_exc()
    exit(1)

# Separate file creation as per ingress name
# Uploading those files under respective s3 directory
for proxy_list in proxy_upstream_list:
    logging.info("Processing logs for {}".format(proxy_list))
    for i in response['data']['result']:
        if str(i['stream']['proxy_upstream_name']).strip("[]") == proxy_list:
            temp_list1.append(i['stream'])
    temp_list2.append({
        proxy_list: temp_list1
    })
    date_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    filename = "{}-{}.log".format(proxy_list, date_time)
    logging.info("-----------------------------------------------------------")
    logging.info("Writing the logs of {} in {}".format(proxy_list, filename))
    dump_to_json(filename, temp_list2)
    upload_to_s3(filename, proxy_list, datetime.today())

    temp_list2.clear()
    temp_list1.clear()
