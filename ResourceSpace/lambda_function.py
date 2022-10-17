#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import json
import os
import urllib
import urllib.request


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

def callAPI(params):
    webURL = urllib.request.urlopen(os.getenv("BASE_URL") + "?" + urllib.parse.urlencode(params, doseq=False))
    data = webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    response = json.loads(data.decode(encoding))
    return response

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
        response = callAPI(params)

        for i in response:
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
                response = callAPI(params)
                resource.update({"name": response, "path": event.get("path")})
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
        response = callAPI(params)

        for i in response:
            resource = {"name": i.get("field8"), "reference": i.get("ref")}
            resourceArray.append(resource)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": resourceArray}),
        }
    return {"statusCode": 404}
