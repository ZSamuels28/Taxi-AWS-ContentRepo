<a href="https://www.messagebird.com/"><img src="https://www.messagebird.com/img/logo.svg" width="200px"/></a><br />
<a href="https://www.taxiforemail.com/"><img src="http://taxiforemail.com/assets/taxiforemail-blue-transparent.png" width="200px"/></a>

# Taxi AWS Content Repository
This repository is for AWS lambda scripts that will allow for Taxi for Email to work with specific Content Repositories

The following readme will go through how to set up a content repository for Taxi for Email using 2 asset management systems, **ResourceSpace** and **Amazon S3**. 

*Note these will require using AWS API Gateway and AWS Lambda.*

<a href="https://github.com/ZSamuels28/Taxi-AWS-ContentRepo#amazon_s3">Creating a Content Repository in Taxi using Amazon S3</a><br />
<a href="https://github.com/ZSamuels28/Taxi-AWS-ContentRepo#resourcespace">Creating a Content Repository in Taxi using ResourceSpace</a>

----------------------------------
<!----><a name="amazon_s3"></a>
## Amazon S3

1. Create an S3 bucket to be used as a content repository. If you would like you can create a folder **content** and put the content within there, however, everything in the S3 bucket will be pulled into the repository. *You will need to have these objects be public as we will need to access them directly via their URLs*

2. Once the S3 bucket is created and populated with a few items, go to AWS Lambda and create a new function. Add a title of the function, choose Runtime Python 3.8, and leave the rest as defaults. *You will need to allow the execution role to read from S3 buckets, so if you already have an IAM Lambda Execution role with S3 Read permissions, you can use it, otherwise modify the role via the next step*

3. Once the function is created, click on **Configuration** and go to **Permissions**. Here you will see the execution role that this Lambda function is using. Click on this role to be taken to the IAM management console. Attach the policy for S3 Read Only access to this role.

4. Go back to the Lambda function and within **Configurations** go to **Environment variables**. Here add a variable **BUCKET_NAME** and set that equal to your S3 bucket in which you will be pulling content from.

5. Go to the **Code** section within the Lambda function and paste the code found within the S3 folder of this repo. Save and deploy the code.

6. Go to the API Gateway service and create a new *REST API where you gain complete control over the request and response along with API management capabilities.* Create two resources: **get-object-url** and **get-objects**, do not check the Configure as proxy resource box. Note: If you need quicker API calls, you can cache the API responses by utilizing API caching: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html

7. Create a **GET** method under each of these resources, check the box for *Use Lambda Proxy integration*, and attach the Lambda Function to each of these methods.

8. Go to actions -> deploy API, and create a Deployment stage (note this will impact your URL). For example, if your deployment stage is Prod, then your API URL would be https://[AWS-API-URL].amazonaws.com/Prod/get-objects

9. Go back to your Lambda function and now you should see API Gateway in the Function Overview.

10. Test out the API by going to **Configuration**, grabbing the API Endpoint for get-objects, and putting it directly into a browser (or clicking on it). If you have objects in your S3 bucket, this should return a response. From there you can test get-object-url by grabbing an ETag from the get-objects, and testing with the URL https://[AWS-API-URL].amazonaws.com/[DeploymentStage]/get-object-url?ETag=[ETag]

11. If you would like to add an authorizer via a lambda function to this API in order to secure it, please see the following video: https://www.youtube.com/watch?v=al5I9v5Y-kA

12. Now we can begin the configuration within Taxi.

13. Login to Taxi for Email (https://taxiforemail.com/) and go to the **Dynamic Content** section. Click on **Feeds** and add a new **Custom** feed.

14. The following information should be added under setup:
    - Data Type: JSON
    - Method (For the method add the following (replace the [AWS-API-URL] with your API url and [DeploymentStage] with the deployment stage):
      ```
      https://[AWS-API-URL].amazonaws.com/[DeploymentStage]/get-object-url?etag={{params.etag}}
      ```
    - Headers (If you added an authorization token per step 11), add the header here
    - Parameters:
      - Parameter name: etag
      - Type: text
      - Default value: (Enter any value you would like this to default to)
    - Data Items:
      - URL: {{json.body.first.Url}}
      - Name: {{json.body.first.Name}}

15. Save and click Test. If the etag parameter you put is valid, you should receive a response.

16. Go to **Search helpers** and create a new Search Helper.

17. The following information should be added under setup of the Search Helper:
    - Data Type: JSON
    - Headers (If you added an authorization token per step 11), add the header here
    - Settings:
      - Press button to show options
    - Result selection
      ```liquid
      {% for item in json.body%}
      {% result %}
      {{- item.ETag -}} : {{item.Name}}
      {% endresult %}
      {% endfor %}
      ```
    - URL pattern
      ```
      https://[AWS-API-URL].amazonaws.com/[DeploymentStage]/get-objects
      ```

18. Save and click Test. Click Search For Feed Data and you should get a list of names from your S3 bucket. Click on one of the items in the list and the Result should populate as the Etag.

19. Next, create (or modify) an Email Design System that contains this feed. Go to **Email Design Systems** and click Add New.

20. Add the Email Design System found in the S3 folder of this repository.

21. Once the Email Design System is uploaded, go to **Feeds** and click on the mz[header].modules[header]. You should see the ability to now map the feed you created as well as the data items. Make sure the Parameter name etag is changed to use a helper value and use the helper you created in step 17.

22. Create a new mailing, add the header module and then click Search For Feed Data. This should now show all of your resources in the S3 bucket. When you click on one of these resources, the image and title should populate.

### Advanced Steps: Adding a Cloudfront Cache
1) See https://medium.com/@tsubasakondo_36683/serve-images-with-cloudfront-s3-8691d5c387b6 for creating a CloudFront distribution. Ensure you can access the CloudFront URLs publicly.

2) In the Lambda function, modify line objects in line 17 and line 35, where the "Url" value should be equal to your CloudFront url + key["key"]. For example:
```python
    object = {
        "Name": os.path.splitext(os.path.basename(key["Key"]))[0],
        "Url": "https://[CLOUDFRONTURL]/"
        + key["Key"],
    }
```

3) Save and deploy and this should now be using your CloudFront distribution to cache images

----------------------------------
<!----><a name="resourcespace"></a>
## ResourceSpace

1. Create a ResourceSpace account to be used as a content repository (https://www.resourcespace.com/). Once you have created an account, you will get a custom ResourceSpace domain to login to. Once logged in, you can upload content. Once content is uploaded, ensure that it is public by accessing the image URL of one of the uploads.

2. After items are uploaded, ensure they have proper Titles, as this is what will be pulled into a Taxi list.

3. Go into ResourceSpace Admin -> Users -> Edit (the user you would like to utilize the API). Scroll down and there will be a Private API key. Keep note of this for later.

3. Once the ResourceSpace repository is ready, go to AWS Lambda and create a new function. Add a title of the function, choose Runtime Python 3.8, and leave the rest as defaults.

4. Go back to the Lambda function and within **Configurations** go to **Environment variables**. Here add the following variables:
   - BASE_URL
     - Note you will need to replace [RESOURCESPACE_URL] with your personal ResourceSpace URL, for example https://ztest.free.resourcespace.com 
     - https://[RESOURCESPACE_URL]/api/index.php
   - PRIVATE_KEY
     - This is the key you copied in step 3
   - USER
     - The username of the user which you edited in step 3, for example admin

5. Go to the **Code** section within the Lambda function and paste the code found within the ResourceSpace folder of this repo. Save and deploy the code.

6. Go to the API Gateway service and create a new *REST API where you gain complete control over the request and response along with API management capabilities.* Create two resources: **get-all-resources** and **get-resource**, do not check the Configure as proxy resource box. Note: If you need quicker API calls, you can cache the API responses by utilizing API caching: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html

7. Create a **GET** method under each of these resources, check the box for *Use Lambda Proxy integration*, and attach the Lambda Function to each of these methods.

8. Go to actions -> deploy API, and create a Deployment stage (note this will impact your URL). For example, if your deployment stage is Prod, then your API URL would be https://[AWS-API-URL].amazonaws.com/Prod/get-all-resources

9. Go back to your Lambda function and now you should see API Gateway in the Function Overview.

10. Test out the API by going to **Configuration**, grabbing the API Endpoint for get-all-resources, and putting it directly into a browser (or clicking on it). If you have objects in your ResourceSpace repository, this should return a response. From there you can test get-resource by grabbing a reference from the get-all-resources, and testing with the URL https://[AWS-API-URL].amazonaws.com/[DeploymentStage]/get-resource?referenceID=[reference]

11. If you would like to add an authorizer via a lambda function to this API in order to secure it, please see the following video: https://www.youtube.com/watch?v=al5I9v5Y-kA

12. Now we can begin the configuration within Taxi.

13. Login to Taxi for Email (https://taxiforemail.com/) and go to the **Dynamic Content** section. Click on **Feeds** and add a new **Custom** feed.

14. The following information should be added under setup:
    - Data Type: JSON
    - Method (For the method add the following (replace the [AWS-API-URL] with your API url and [DeploymentStage] with the deployment stage):
      ```
      https://[AWS-API-URL].amazonaws.com/[DeploymentStage]/get-resource?referenceID={{params.reference}}
      ```
    - Headers (If you added an authorization token per step 11), add the header here
    - Parameters:
      - Parameter name: referenceID
      - Type: text
      - Default value: (Enter any value you would like this to default to)
    - Data Items:
      - URL: {{json.body.first.url}}
      - Name: {{json.body.first.name}}

15. Save and click Test. If the etag parameter you put is valid, you should receive a response.

16. Go to **Search helpers** and create a new Search Helper.

17. The following information should be added under setup of the Search Helper:
    - Data Type: JSON
    - Headers (If you added an authorization token per step 11), add the header here
    - Settings:
      - Press button to show options
    - Result selection
      ```liquid
      {% for item in json.body%}
      {% result %}
      {{- item.reference -}} : {{item.name}}
      {% endresult %}
      {% endfor %}
      ```
    - URL pattern
      ```
      https://[AWS-API-URL].execute-api.us-west-2.amazonaws.com/[[DeploymentStage]/get-all-resources
      ```

18. Save and click Test. Click Search For Feed Data and you should get a list of names from your ResourceSpace content repository. Click on one of the items in the list and the Result should populate as the referenceID.

19. Next, create (or modify) an Email Design System that contains this feed. Go to **Email Design Systems** and click Add New.

20. Add the Email Design System found in the ResourceSpace folder of this repository.

21. Once the Email Design System is uploaded, go to **Feeds** and click on the mz[header].modules[header]. You should see the ability to now map the feed you created as well as the data items. Make sure the Parameter name referenceID is changed to use a helper value and use the helper you created in step 17.

22. Create a new mailing, add the header module and then click Search For Feed Data. This should now show all of your resources in the ResourceSpace repository. When you click on one of these resources, the image and title should populate.
