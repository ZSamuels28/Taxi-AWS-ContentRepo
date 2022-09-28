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

6. Go to the API Gateway service and create a new *REST API where you gain complete control over the request and response along with API management capabilities.* Create two resources: **get-object-url** and **get-objects**, do not check the Configure as proxy resource box.

7. Create a **GET** method under each of these resources, check the box for *Use Lambda Proxy integration*, and attach the Lambda Function to each of these methods.

8. Go to actions -> deploy API, and create a Deployment stage (note this will impact your URL). For example, if your deployment stage is Prod, then your API URL would be https://[AWS-API-URL]/Prod/get-objects

9. Go back to your Lambda function and now you should see API Gateway in the Function Overview.

10. Test out the API by going to **Configuration**, grabbing the API Endpoint for get-objects, and putting it directly into a browser (or clicking on it). If you have objects in your S3 bucket, this should return a response. From there you can test get-object-url by grabbing an ETag from the get-objects, and testing with the URL https://[AWS-API-URL]/[DeploymentStage]/get-object-url?ETag=[ETag]

11. If you would like to add an authorizer via a lambda function to this API in order to secure it, please see the following video: https://www.youtube.com/watch?v=al5I9v5Y-kA

12. Now we can begin the configuration within Taxi.

13. Login to Taxi for Email (https://taxiforemail.com/) and go to the **Dynamic Content** section. Click on **Feeds** and add a new **Custom** feed.

14. The following information should be added under setup:
    - Data Type: JSON
    - Method (For the method add the following (replace the [AWS-API-URL] with your API url):
      ```
      https://[AWS-API-URL].amazonaws.com/Test/get-object-url?etag={{params.etag}}
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
      https://[AWS-API-URL].execute-api.us-west-2.amazonaws.com/Test/get-objects
      ```

18. Save and click Test. Click Search For Feed Data and you should get a list of names from your S3 bucket. Click on one of the items in the list and the Result should populate as the Etag.

19. Next, create (or modify) an Email Design System that contains this feed. Go to **Email Design Systems** and click Add New.

20. Add the Email Design System found in the S3 folder of this repository.

21. Once the Email Design System is uploaded, go to **Feeds** and click on the mz[header].modules[header]. You should see the ability to now map the feed you created as well as the data items. Make sure the Parameter name etag is changed to use a helper value and use the helper you created in step 17.

22. Create a new mailing, add the header module and then click Search For Feed Data. This should now show all of your resources in the S3 bucket. When you click on one of these resources, the image and title should populate.

## ResourceSpace
