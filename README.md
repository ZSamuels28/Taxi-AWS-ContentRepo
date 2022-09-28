<a href="https://www.messagebird.com/"><img src="https://www.messagebird.com/img/logo.svg" width="200px"/></a><br />
<a href="https://www.taxiforemail.com/"><img src="http://taxiforemail.com/assets/taxiforemail-blue-transparent.png" width="200px"/></a>

# Taxi AWS Content Repository
This repository is for AWS lambda scripts that will allow for Taxi for Email to work with specific Content Repositories

The following readme will go through how to set up a content repository for Taxi for Email using 2 asset management systems, **ResourceSpace** and **Amazon S3**. 

*Note these will require using AWS API Gateway and AWS Lambda.*

## Amazon S3

1. Create an S3 bucket to be used as a content repository. If you would like you can create a folder **content** and put the content within there, however, everything in the S3 bucket will be pulled into the repository. *You will need to ensure these assets are public otherwise Taxi will not be able to see them.* The following bucket policy can be used to make the S3 bucket public (note you will need to replace the ARN):

2. Access AWS Lambda and create a new function. Title the function, choose Runtime Python 3.8, and leave the rest of the defaults. *You will need to allow the execution role to read from S3 buckets, so if you already have an IAM Lambda Execution role with these permissions, you can use it, otherwise modify the role via the next step*

3. Once the function is created, click on **Configuration** and go to **Permissions**. Here you will see the execution role that Lambda is using. Click on this role to be taken to the IAM management console. Attach the policy for S3 Read Only access to this role.

4. Go back to the Lambda function in **Configurations** and go to **Environment variables**. Here add a variable BUCKET_NAME and set that equal to your S3 bucket in which you will be pulling content from.

5. Go to **Code** within the Lambda function and paste the code found within the S3 folder of this repo. Save and deploy the code.

6. We will need to create 2 API calls to be able to access this Lambda function - **get-object-url** and **get-objects**

7. Go to the API Gateway service and create a new *REST API where you gain complete control over the request and response along with API management capabilities.* Create two resources with no authentication: **get-object-url** and **get-objects**

8. Create a **GET** method under each of these resources, check the box for *Use Lambda Proxy integration*, and attach the Lambda Function to each of these methods.
<img width="200" src="https://user-images.githubusercontent.com/8294014/192674274-1d58e65b-19d4-415a-8189-a9579b195869.png">

9. Go to actions -> deploy API, and create a Deployment stage (note this will impact your URL). For example, if your deployment stage is Prod, then your API call would be https://[AWS-API-URL]/Prod/get-objects

10. Go back to your Lambda function and now you should see API Gateway now in the Function Overview.

11. Test out the API by going to **Configuration**, grabbing the API Endpoint for get-objects, and putting it directly into a browser (or clicking on it). If you have objects in your S3 bucket, this should return a response. From there you can test get-object-url by grabbing an ETag from the get-objects, and testing with the URL https://[AWS-API-URL]/[DeploymentStage]/get-object-url?ETag=[ETag]

12. Now we can begin the configuration within Taxi.



## ResourceSpace
