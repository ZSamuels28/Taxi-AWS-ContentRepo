import json
import boto3
import os

# Pulls the env variables directly with os.getenv("ENV_KEY_NAME")
# AWS_KEY_ID
# AWS_SECRET
# BUCKET_NAME
#
# Loops through to get all objects from the bucket to obtain "Key". Checks the file size is not equal to 0 and returns a JSON response with ETag key and value of the URL
# Filename is probably better than ETag. Have to strip the "content/"" from 'Key': 'content/11439.png'
#

def lambda_handler(event, context):
    s3 = boto3.client("s3", region_name="us-west-2", aws_access_key_id=os.getenv("AWS_KEY_ID"),aws_secret_access_key=os.getenv("AWS_SECRET"))
    obj_list = (s3.list_objects_v2(Bucket=os.getenv("BUCKET_NAME")))
    objects = []
    response = {}
    
    if event.get("path") == "/get-object-url":
        etag = event.get("queryStringParameters").get("etag")
        for key in obj_list['Contents']:
            if key['ETag'].replace('"', '') == etag:
                object = {'Name' : os.path.splitext(os.path.basename(key['Key']))[0], 'Url' : 'https://' + os.getenv("BUCKET_NAME") + '.s3.amazonaws.com/' + key['Key']}
                objects.append(object)
                return { "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({'body' : objects})
                    }
        return { "statusCode": 400,
        'body' : json.dumps('Something went wrong')
        }
    
    elif event.get("path") == "/get-objects":
        for key in obj_list['Contents']:
            if key['Size'] != 0:
                print(key)
                object = {'Name' : os.path.splitext(os.path.basename(key['Key']))[0], 'ETag' : key['ETag'].replace('"', ''), 'Url' : 'https://' + os.getenv("BUCKET_NAME") + '.s3.amazonaws.com/' + key['Key']}
                objects.append(object)
        return { 
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'body' : objects})
            }
    else:
        return { "statusCode": 404,
        'body' : json.dumps('Endpoint not found')
        }