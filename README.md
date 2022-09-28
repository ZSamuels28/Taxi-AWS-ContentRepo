<a href="https://www.messagebird.com/"><img src="https://www.messagebird.com/img/logo.svg" width="200px"/></a><br />
<a href="https://www.taxiforemail.com/"><img src="http://taxiforemail.com/assets/taxiforemail-blue-transparent.png" width="200px"/></a>

# Taxi AWS Content Repository
This repository is for AWS lambda scripts that will allow for Taxi for Email to work with specific Content Repositories

The following readme will go through how to set up a content repository for Taxi for Email using 2 asset management systems, **ResourceSpace** and **Amazon S3**. 

*Note these will require using AWS API Gateway and AWS Lambda.*

## Amazon S3

1. Create an S3 bucket to be used as a content repository. If you would like you can create a folder **content** and put the content within there, however, everything in the S3 bucket will be pulled into the repository. *You will need to ensure these assets are public otherwise Taxi will not be able to see them.*

2. Once the S3 bucket is created and populated with a few items, go to AWS Lambda and create a new function. Add a title of the function, choose Runtime Python 3.8, and leave the rest as defaults. *You will need to allow the execution role to read from S3 buckets, so if you already have an IAM Lambda Execution role with S3 Read permissions, you can use it, otherwise modify the role via the next step*

3. Once the function is created, click on **Configuration** and go to **Permissions**. Here you will see the execution role that this Lambda function is using. Click on this role to be taken to the IAM management console. Attach the policy for S3 Read Only access to this role.

4. Go back to the Lambda function and within **Configurations** go to **Environment variables**. Here add a variable **BUCKET_NAME** and set that equal to your S3 bucket in which you will be pulling content from.

5. Go to the **Code** section within the Lambda function and paste the code found within the S3 folder of this repo. Save and deploy the code.

6. Go to the API Gateway service and create a new *REST API where you gain complete control over the request and response along with API management capabilities.* Create two resources with no authentication: **get-object-url** and **get-objects**

7. Create a **GET** method under each of these resources, check the box for *Use Lambda Proxy integration*, and attach the Lambda Function to each of these methods.
<img width="200" src="https://user-images.githubusercontent.com/8294014/192674274-1d58e65b-19d4-415a-8189-a9579b195869.png">

8. Go to actions -> deploy API, and create a Deployment stage (note this will impact your URL). For example, if your deployment stage is Prod, then your API URL would be https://[AWS-API-URL]/Prod/get-objects

9. Go back to your Lambda function and now you should see API Gateway in the Function Overview.

10. Test out the API by going to **Configuration**, grabbing the API Endpoint for get-objects, and putting it directly into a browser (or clicking on it). If you have objects in your S3 bucket, this should return a response. From there you can test get-object-url by grabbing an ETag from the get-objects, and testing with the URL https://[AWS-API-URL]/[DeploymentStage]/get-object-url?ETag=[ETag]

11. Now we can begin the configuration within Taxi.


## ResourceSpace
