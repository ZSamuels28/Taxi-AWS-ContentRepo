#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import boto3
import os


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    obj_list = s3.list_objects_v2(Bucket=os.getenv("BUCKET_NAME"))
    objects = []
    response = {}

    if event.get("path") == "/get-object-url":
        etag = event.get("queryStringParameters").get("etag")
        for key in obj_list["Contents"]:
            if key["ETag"].replace('"', "") == etag:
                object = {
                    "Name": os.path.splitext(os.path.basename(key["Key"]))[0],
                    "Url": "https://"
                    + os.getenv("BUCKET_NAME")
                    + ".s3.amazonaws.com/"
                    + key["Key"],
                }
                objects.append(object)
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"body": objects}),
                }
        return {"statusCode": 400, "body": json.dumps("Something went wrong")}
    elif event.get("path") == "/get-objects":

        for key in obj_list["Contents"]:
            if key["Size"] != 0:
                object = {
                    "Name": os.path.splitext(os.path.basename(key["Key"]))[0],
                    "ETag": key["ETag"].replace('"', ""),
                    "Url": "https://"
                    + os.getenv("BUCKET_NAME")
                    + ".s3.amazonaws.com/"
                    + key["Key"],
                }
                objects.append(object)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": objects}),
        }
    else:
        return {"statusCode": 404, "body": json.dumps("Endpoint not found")}
