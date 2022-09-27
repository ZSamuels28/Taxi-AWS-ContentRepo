import requests, hashlib, json, os

def getConfig():
    cfg = {
        "base_url": os.getenv("BASE_URL", ""),
        "private_key": os.getenv("PRIVATE_KEY", ""),
        "user": os.getenv("USER", ""),
    }
    return cfg

def signString(query_string):
    cfg = getConfig()
    return hashlib.sha256(
        (cfg.get("private_key") + query_string).encode("utf-8")
    ).hexdigest()


def lambda_handler(event, context):
    cfg = getConfig()

    if event.get("path") == "/get-resource":
        resourceArray = []
        referenceID = event.get("queryStringParameters").get("referenceID")
        query = (
            "user="
            + cfg.get("user")
            + "&function=get_resource_all_image_sizes&resource="
            + referenceID
        )
        response = requests.get(
            cfg.get("base_url")
            + "/api/index.php/?"
            + query
            + "&sign="
            + signString(query)
        )

        for i in response.json():
            if i.get("size_code") == "original":
                resource = {"referenceID": referenceID, "url": i.get("url")}

                query = (
                    "user="
                    + cfg.get("user")
                    + "&function=get_data_by_field&field=8&ref="
                    + referenceID
                )
                response = requests.get(
                    cfg.get("base_url")
                    + "/api/index.php/?"
                    + query
                    + "&sign="
                    + signString(query)
                )

                resource.update({"name": response.json(), "path": event.get("path")})
                resourceArray.append(resource)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": resourceArray}),
        }

    elif event.get("path") == "/get-all-resources":
        resourceArray = []
        query = "user=" + cfg.get("user") + "&function=search_get_previews&search=*"
        response = requests.get(
            cfg.get("base_url")
            + "/api/index.php/?"
            + query
            + "&sign="
            + signString(query)
        )

        for i in response.json():
            resource = {"name": i.get("field8"), "reference": i.get("ref")}
            resourceArray.append(resource)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"body": resourceArray}),
        }

    return {"statusCode": 404}