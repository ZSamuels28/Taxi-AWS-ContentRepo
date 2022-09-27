#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import hashlib
import json
import os
import urllib


def buildQuery(**params):
    queryString = urllib.parse.urlencode(params, doseq=False)
    params.update(
        {
            "sign": hashlib.sha256(
                (os.getenv("PRIVATE_KEY") + queryString).encode("utf-8")
            ).hexdigest()
        }
    )
    return params


def lambda_handler(event, context):

    if event.get("path") == "/get-resource":
        resourceArray = []
        referenceID = event.get("queryStringParameters").get("referenceID")
        params = buildQuery(
            **{
                "user": os.getenv("USER"),
                "function": "get_resource_all_image_sizes",
                "resource": referenceID,
            }
        )
        response = requests.get(os.getenv("BASE_URL"), params=params)

        for i in response.json():
            if i.get("size_code") == "original":
                resource = {"referenceID": referenceID, "url": i.get("url")}
                params = buildQuery(
                    **{
                        "user": os.getenv("USER"),
                        "function": "get_data_by_field",
                        "field": "8",
                        "ref": referenceID,
                    }
                )
                response = requests.get(os.getenv("BASE_URL"), params=params)
                resource.update({"name": response.json(), "path": event.get("path")})
                resourceArray.append(resource)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": resourceArray}),
        }
    elif event.get("path") == "/get-all-resources":

        resourceArray = []
        params = buildQuery(
            **{
                "user": os.getenv("USER"),
                "function": "search_get_previews",
                "search": "*",
            }
        )
        response = requests.get(os.getenv("BASE_URL"), params=params)

        for i in response.json():
            resource = {"name": i.get("field8"), "reference": i.get("ref")}
            resourceArray.append(resource)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": resourceArray}),
        }
    return {"statusCode": 404}
