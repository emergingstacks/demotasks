import boto3
import os
import docker
from git.repo.base import Repo
import random

import base64

client = docker.from_env()
repo_url = "https://github.com/harshalk91/democi.git"
destination_dir = "/tmp/democi"
ecr_client = boto3.client('ecr', region_name='us-east-1')
docker_repo_url = "745946109524.dkr.ecr.us-east-1.amazonaws.com/democi"


def clone_repo(repo_name, dest_dir):
    if os.path.exists(dest_dir):
        print("Already exists")
    else:
        Repo.clone_from(repo_name, dest_dir)


def build_docker_image(dest_dirc, docker_image_url):
    print("Building docker image")
    hash = random.getrandbits(128)
    client.images.build(path="/tmp/democi", tag=docker_image_url + ":latest")
    client.images.build(path="/tmp/democi", tag="{}:{}".format(docker_image_url, hash))
    return [str(hash), "latest"]


def upload_image_to_ecr(docker_image_url, image_tags):
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']
    auth_config = {'username': username, 'password': password}
    print("logging to ec2")
    client.login(username, password, registry=registry)
    print("pushing the image")
    for tag in image_tags:
        client.images.push(docker_image_url+":"+tag, auth_config=auth_config)


clone_repo(repo_url, destination_dir)
image_tags = build_docker_image(destination_dir, docker_repo_url)
upload_image_to_ecr(docker_repo_url, image_tags)
