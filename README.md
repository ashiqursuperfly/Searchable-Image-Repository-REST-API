## Searchable Image Repository REST API

### Table of Contents
- [**`Core Features`**](#core-features)
- [**`Implementation Details`**](#implementation-details)
- [**`API Documentation`**](#api-documentation)
    - [Getting an Authentication Token](#getting-an-authentication-token)
    - [Upload Image(s)](#upload-images)
        - Single Image Upload
        - Bulk Image Upload
    - [Search](#search)
        - Full Text Search
        - Image Search
    - [Fetching Async Task Results](#fetching-async-task-results)  
    - [Error Handling](#error-handling)
- [**`URL based Image Manipulation`**](#url-based-image-manipulation)
- [**`Local Installation Guidelines`**](#local-installation-guidelines)


### Core Features
- handles single and bulk image uploads with minimal response time
- url based image manipulation to resize images on the fly
- serving images through cdn
- two types of image searching is available.
    - i. **Full Text Search** (user enters some keywords or a phrase or a country location)
    - ii. **Image Search** (user enters an image, optionally can also enter full text search parameters that aid narrow down the search space)
- access protection, users can only delete images uploaded by him/her


### Implementation Details
- built using [**`Django Rest Framework`**](https://www.django-rest-framework.org/)
- uses [**`RabbitMQ`**](https://www.rabbitmq.com/) as message broker and [**`Celery`**](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) as synchronous task queue to carry out long tasks, resulting in minimal response time for bulk image upload
- uses [**`PostgreSQL Full Text Search`**](https://www.postgresql.org/docs/13/textsearch.html) to perform full text search of images based on image meta  
- extracts [**`ORB`**](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html) descriptors from images and uses open cv based matcher for image search
- images are stored in **AWS S3** storage
- images are served through **AWS Cloudfront CDN**
- **URL based Image Manipulation** is available through an **AWS Lambda** function
- served through **nginx** on an **AWS EC2** instance. [Deployed Here](http://ec2-18-220-183-110.us-east-2.compute.amazonaws.com/api/doc)


### API Documentation
<a href="http://ec2-18-220-183-110.us-east-2.compute.amazonaws.com/api/doc"><img src="https://raw.githubusercontent.com/swagger-api/swagger.io/wordpress/images/assets/SWU-logo-clr.png" width="200"></a>

This API documentation explains **some** important endpoints in detail. Find the **full** **Swagger UI** documentation available here: [**Click Here**](http://ec2-18-220-183-110.us-east-2.compute.amazonaws.com/api/doc)

### Getting an Authentication Token
#### **`POST`** **api/signup**
Hitting the endpoint with the following request body would register a user with this email. This endpoint can be used only once with the same username and email. Check [**`POST`** **api/api-token-auth**](#post-apiapi-token-auth) to retrieve a registered user's auth token.

Request Body:
```yml
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```
Example **HTTP 200** Response:
```yml
{
  "detail": "success",
  "content": {
    "email": "user@example.com",
    "username": "string",
    "password": "string",
    "token": "be151b8865d43783fa80cd147ff0df472395d340"
  }
}
```
#### **`POST`** **api/api-token-auth**
Request Body:
```yml
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```
Example **HTTP 200** Response:
```yml
{
  "token": "string"
}
```
This `token` can be used as the `bearer` token in the http `authorization` header to authenticate some non-public endpoints.
### Upload Image(s)
#### **`POST`** **api/images**
**ContentType** of this request must be **multipart/form-data** . This is general for all endpoints accepting an image file binary.

Header:
```yml
auth: Bearer <token>
```
Request Body:
```yml
{
  "img": <image_file_binary>,
  "country": "2-digit-country-code", # use the GET /api/country endpoint for a list of options
  "description": "image caption",
  "categories": [
    <category_ids> # use the GET /api/images/categories endpoint for a list of options
  ]
}
```
Example **HTTP 200** Response:
```yml
{
  "detail": "You request is being processed. You can check the status of your request using the /task-result/{task_id} endpoint",
  "content": {
    "<task_id>": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/bojack-horseman-png" # image url when the upload will be completed
  }
}
```
In the process of uploading to a storage bucket, image features are also generated from the image which is used for image searching. Clients do not need to wait for all this, the API returns a task_id assigned to this image upload task. Clients implementing this can easily query the task_id [**`GET /api/task-result/{task_id}`**](#get-apitask-resulttask_id)** to check if the upload is complete.
#### **`POST`** **api/images/bulk**
**ContentType** of this request must be **multipart/form-data** . This is general for all endpoints accepting an image file binary.

Header:
```yml
auth: Bearer <token>
```
Request Body:
```yml
{
  "images": [
    <image_file_binary>
  ],
  "meta": [
    {
      "country": "2-digit-country-code", # use the GET /api/country endpoint for a list of options,
      "description": "image caption",
      "categories": [
        <category_ids> # use the GET /api/images/categories endpoint for a list of options
      ]
    }
  ]
}
```
The number of items in the **`meta`** array can be either **exactly 1** or **exactly the number of items in `images` array**. In the first case, the single meta properties are applied to all the images in the bulk. In the latter case, meta properties are assigned to the corresponding indexed image in the `images` array. e.g: **meta[i]** is assigned to **images[i]**.

Example **HTTP 200** Response:
```yml
{
  "detail": "You request is being processed. You can check the status of your request using the GET /task-result/{task_id} endpoint",
  "content": [
    {
      "<task_id>": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/bojack-horseman-png" # image url when the upload will be completed
    }
  ]
}
```
The response is similar to the single upload api. However, in this case returns a task_id for each image.
### Search
#### **`POST`** **api/images/full-text-search**
Request Body:
```yml
{
  "phrase": "string",
  "keywords": [
    "string"
  ],
  "country_name_or_code": "string"
}
```
Need to provide at least one of the three fields `phrase`, `keywords`, `country_name_or_code`.

Example **HTTP 200** Response:
```yml
{
  "detail": "success",
  "content": [
    {
      "id": 1,
      "country": {
        "code": "AU",
        "name": "Australia"
      },
      "categories": [
        {
          "id": 1,
          "name": "wallpapers"
        }
      ],
      "owner": {
        "username": "test"
      },
      "img": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/47183395_178349jpg",
      "description": "pop os wallpapers",
      "date_added": "2021-05-07T11:21:54.520145Z",
      "date_modified": "2021-05-07T11:21:54.520159Z"
    }
  ]
}
```
#### **`POST`** **api/images/image-search**
**ContentType** of this request must be **multipart/form-data** . This is general for all endpoints accepting an image file binary.

Request Body:
```yml
{
  "img": <image_file_binary>,
  "phrase": "string",
  "keywords": [
    "string"
  ],
  "country_name_or_code": "string"
}
```
Example **HTTP 200** Response:
```yml
{
  "detail": "You request is being processed. You can check the status of your request using the /task-result/{task_id} endpoint",
  "content": "<task_id>"
}
```
Image Searching can take a while, since it needs to compare the queried image's **ORB Descriptors**. Therefore, this API returns a task_id assigned to this image search task. Clients implementing this can easily query the task_id [**`GET /api/task-result/{task_id}`**](#get-apitask-resulttask_id)** to check if the searching is complete and also, fetch the search results.
### Fetching Async Task Results
#### **`GET /api/task-result/{task_id}`**
`task_id` (a path parameter) value can be found in the image search / upload api responses.

Example **HTTP 200** Response:
```yml
{
  "detail": "success",
  "content": {
    "status": "SUCCESS",
    "result": [
      {
        "img": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/41250564_2_0mdb3d4jpeg",
        "match": 1
      },
      {
        "img": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/19634438_5webp",
        "match": 0.2222222222222222
      },
      {
        "img": "https://d24fj9qq8rdx7g.cloudfront.net/iidb/57189077_5_jyxcpm3webp",
        "match": 0.2222222222222222
      }
    ]
  }
}
```
The field `result` contains the result objects (single image, array of search result images etc)
### Error Handling
All responses follow a generic format both for error and non-error responses. The `detail` field returns a detailed error message of the http error triggered. The `content` field can be ignored for error responses.
```yml
{
  "detail": "string",
  "content": "string"
}
```
Common http errors handled are,

**401 UNAUTHORIZED**
```yml
{
  "detail": "Token invalid/unavailable in header ",
  "content": null
}
```
**422 UNPROCESSABLE ENTITY**
```yml
{
  "detail": "Fields missing in request \"username\", \"password\"",
  "content": null
}
```
**405 METHOD NOT ALLOWED**
```yml
{
  "detail": "Method \"POST\" not allowed.",
  "content": null
}
```
### URL based Image Manipulation
In order to resize an image url of the form: https://d24fj9qq8rdx7g.cloudfront.net/{s3-key}

**1.** You need to create a JSON body of the form:
```yml
{
  "bucket": "crop-disease-debug", # i am using the same s3 bucket as one of my other projects for now :)
  "key": <s3-key>,
  "edits": {
    "resize": {
      "width": 120,
      "height": 120,
      "fit": ("cover" or "contain" or "fill" or "inside" or "outside"),
      "background": {
        "r": 255,
        "g": 255,
        "b": 0,
        "alpha": 1
      }
    },
    "grayscale": true,
    "flip": true,
    "flop": true,
    "negate": true,
    "flatten": true,
    "normalise": true,
    "smartCrop": {
      "padding": 12
    }
  }
}
```
All keys under the `edits` key are optional. It all depends on the edits you want to perform to the image. There are a lot of powerful modifications (like `resize`, `grayscale`, `negate`, `add a background`, `crop`) you can do to the image just by manipulating the url.

**2.** Now, convert the JSON body into a **BASE 64** string.

**3.** Finally, append the base 64 string to the cloudfront base url like so: **https://d24fj9qq8rdx7g.cloudfront.net/{base-64-of-json-body}**
### Local Installation Guidelines
The project is fully dockerized, so it is very easy to start up the required containers from the docker-compose.yml file in the project root. All you need is docker and docker-compose installed in the system.
```
docker-compose up --build
```
However, This project requires some cloud resources like (AWS S3 file storage) in order to function properly. So, in order to run the project locally you need to have a **.debug.env** file in the project root which should look like the following:
```
DEBUG=1
DJANGO_APP_SECRET_KEY=anything
AWS_ACCESS_KEY_ID=****
AWS_SECRET_ACCESS_KEY=****
AWS_S3_REGION_NAME=****
AWS_STORAGE_BUCKET_NAME=****
AWS_CLOUDFRONT_DOMAIN=****
ALLOWED_HOSTS=127.0.0.1,localhost
RABBITMQ_DEFAULT_USER=anything
RABBITMQ_DEFAULT_PASS=anything
POSTGRES_USER=anything
POSTGRES_PASSWORD=anything
POSTGRES_DB=anything
```
The API is deployed for demonstration here [http://ec2-18-220-183-110.us-east-2.compute.amazonaws.com/api/doc](http://ec2-18-220-183-110.us-east-2.compute.amazonaws.com/api/doc) so, it is of course not necessary to run the project locally in order to test out the features. You can easily use the **Swagger UI** to try out the endpoints.
