# -*- coding: utf-8 -*-
import json
import os

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tcr.v20190924 import tcr_client, models

cred = credential.Credential(os.getenv("SECRET_ID"), os.getenv("SECRET_KEY"))
httpProfile = HttpProfile()
httpProfile.endpoint = "tcr.tencentcloudapi.com"

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = tcr_client.TcrClient(cred, "ap-guangzhou", clientProfile)


def list_repo():
    try:
        req = models.DescribeRepositoryOwnerPersonalRequest()
        req.from_json_string(json.dumps({}))
        resp = client.DescribeRepositoryOwnerPersonal(req)
        return resp
    except TencentCloudSDKException as err:
        print(err)


def create_repo(name):
    try:
        req = models.CreateRepositoryPersonalRequest()
        req.from_json_string(json.dumps({
            "RepoName": "acejilam/" + name,
            "Public": 1
        }))
        resp = client.CreateRepositoryPersonal(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)


def delete_repo(name):
    try:
        req = models.DeleteRepositoryPersonalRequest()
        params = {
            "RepoName": name
        }
        req.from_json_string(json.dumps(params))
        resp = client.DeleteRepositoryPersonal(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)


if __name__ == '__main__':
    for item in list_repo().Data.RepoInfo:
        if item.Public != 1:
            delete_repo(item.RepoName)
