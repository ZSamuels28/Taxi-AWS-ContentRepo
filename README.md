<a href="https://www.messagebird.com/"><img src="https://www.messagebird.com/img/logo.svg" width="200px"/></a><br />
<a href="https://www.taxiforemail.com/"><img src="http://taxiforemail.com/assets/taxiforemail-blue-transparent.png" width="200px"/></a>

# Taxi AWS Content Repository
This repository is for AWS lambda scripts that will allow for Taxi for Email to work with specific Content Repositories

The following readme will go through how to set up a content repository for Taxi for Email using 2 asset management systems, **ResourceSpace** and **Amazon S3**. 

*Note these will require using AWS API Gateway and AWS Lambda.*

## Amazon S3

1. Create an S3 bucket to be used as a content repository. If you would like you can create a folder **content** and put the content within there, however, everything in the S3 bucket will be pulled into the repository. *You will need to ensure these assets are public otherwise Taxi will not be able to see them.* The following bucket policy can be used to make the S3 bucket public (note you will need to replace the ARN):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "REPLACE_WITH_ARN/*"
        }
    ]
}
```
<img src="https://user-images.githubusercontent.com/8294014/192653257-a6a082a7-86f1-4ea0-a43c-9021b6fd8894.png" width="550" height="200">

2. Now go into AWS Lambda and create a new function. Title the function, choose Runtime Python 3.8, and leave the rest of the defaults.

## ResourceSpace
