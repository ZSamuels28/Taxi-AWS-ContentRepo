#!/usr/bin/env python3
import os, json, boto3, time, urllib3
from urllib.parse import urljoin, urlencode
from boto3.dynamodb.conditions import Key

# Persistent token, uses DynamoDB for storage
class PersistentAuthToken:
    def __init__(self, et_subdomain: str, et_clientID: str, et_clientSecret: str):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(os.getenv("dynamo_db_table"))
        self.tokPrefix = "sfmc_taxi:"
        self.tokName = "access_token"
        # Collect auth params
        if et_subdomain:
            self.et_url = urljoin(
                "https://" + et_subdomain + ".auth.marketingcloudapis.com", "/v2/token"
            )
        else:
            raise ValueError("Parameter et_subdomain not defined")
        if et_clientID:
            self.et_clientID = et_clientID
        else:
            raise ValueError("Parameter et_clientID not defined")
        if et_clientSecret:
            self.et_clientSecret = et_clientSecret
        else:
            raise ValueError("Parameter et_clientSecret not defined")

    def get(self):
        #Checks against DynamoDB table if a session token already exists
        resp = self.table.query(
            KeyConditionExpression=Key("key").eq(self.tokPrefix + self.tokName)
        )
        #If a token exists, checks the TTL (even if DynamoDB TTL is set it can be delayed). If TTL > now delete token and generate a new one.
        if resp["Count"] == 1:
            if resp["Items"][0]["ttl"] < int(time.time()):
                self.table.delete_item(Key={"key": self.tokPrefix + self.tokName})
                self.get()
            else:
                return resp["Items"][0]["access_token"]
        else:
            # Get a fresh token. See https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/access-token-s2s.html
            http = urllib3.PoolManager()
            data = {
                "grant_type": "client_credentials",
                "client_id": self.et_clientID,
                "client_secret": self.et_clientSecret,
            }
            encoded_data = json.dumps(data).encode("utf-8")
            res = http.request(
                "POST",
                self.et_url,
                body=encoded_data,
                headers={"Content-Type": "application/json"},
            )
            if res.status != 200:
                raise ValueError("Authentication error", res.status, res.data)
            else:
                r = json.loads(res.data.decode("utf-8"))
                access_token = r.get(self.tokName)
                expires_in = r.get("expires_in")
                scope = r.get("scope")
                if access_token and expires_in and scope:
                    # safely stop using it 2 mins before it expires
                    self.set(access_token, max(0, expires_in - 120), scope)
                    return access_token
                else:
                    raise ValueError(
                        "Invalid access_token, expires_in, scope returned",
                        access_token,
                        expires_in,
                        scope,
                    )

    def set(self, access_token: str, ttl: int, scope: str):
        self.table.put_item(
            Item={
                "key": self.tokPrefix + self.tokName,
                "access_token": access_token,
                "scope": scope,
                "ttl": int(time.time()) + ttl,
            }
        )


def lambda_handler(event, context):
    et_subdomain = os.getenv("et_subdomain")
    tok = PersistentAuthToken(
        et_subdomain, os.getenv("et_clientID"), os.getenv("et_clientSecret")
    )
    auth = tok.get()
    # Fetch an inventory of images
    asset = []
    page = 1
    if event.get("path") == "/list":
        while True:
            # See https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/assetSimpleQuery.html
            list_assets_url = urljoin(
                "https://" + et_subdomain + ".rest.marketingcloudapis.com",
                "/asset/v1/content/assets",
            )

            # NB SFMC does not accept % encoding on the $filter setting name, so have to force custom encoding
            # It also expects comma and = to be passed through
            # NB filter needs to match on name "image" (lowercase) not "Image"
            p = urlencode(
                {
                    "$page": page,
                    "$pagesize": 400,
                    "$orderBy": "id asc",
                    "$filter": "assetType.displayName=image",
                    "$fields": "id,customerKey,fileProperties,assetType",
                },
                safe="/$=,",
            )
            http = urllib3.PoolManager()
            res = http.request(
                "GET",
                list_assets_url + "?" + p,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(auth),
                },
            )
            if res.status != 200:
                raise ValueError(res.status, res.data)
            else:
                # debug print(curlify.to_curl(res.request))
                resObj = json.loads(res.data.decode("utf-8"))
                if resObj.get("count") > 0:
                    for i in resObj.get("items"):
                        asset.append(i)
                    page += 1
                else:
                    break
        return {"statusCode": 200, "body": json.dumps(asset, indent=2)}
    elif event.get("path") == "/get-item":
        id = event.get("queryStringParameters").get("id")
        # See https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/getObjectById.html
        get_asset_url = urljoin(
            "https://" + et_subdomain + ".rest.marketingcloudapis.com",
            "/asset/v1/content/assets/" + id,
        )
        http = urllib3.PoolManager()
        res = http.request(
            "GET",
            get_asset_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(auth),
            },
        )
        if res.status != 200:
            raise ValueError(res.status, res.data)
        else:
            return {
                "statusCode": 200,
                "body": json.dumps(json.loads(res.data.decode("utf-8"))),
            }
    else:
        return {"statusCode": 404, "body": json.dumps("Endpoint not found")}
