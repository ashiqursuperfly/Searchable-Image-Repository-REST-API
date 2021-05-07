## Searchable Image Repository REST API

### Table of Contents
- [**`Core Features`**](#core-features)
- [**`Implementation Details`**](#implementation-details)
- [**`API Documentation`**](#api-documentation)
    - [Getting an Authentication Token](#getting-an-authentication-token)
    - [Upload Image(s)](#upload-image(s))
        - Single Image Upload
        - Bulk Image Upload
    - [Search](#search)
        - Full Text Search
        - Image Search
    - [Error Handling](#error-handling)
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
- served through **nginx** on an **AWS EC2** instance. [Deployed Here](http://18.220.183.110/api/doc)


### API Documentation
<a href="http://18.220.183.110/api/doc"><img src="https://raw.githubusercontent.com/swagger-api/swagger.io/wordpress/images/assets/SWU-logo-clr.png" width="200"></a>

This API documentation is **partial** and only intended to explain some endpoints in detail. Find the **full** **Swagger UI** documentation available here: [**Click Here**](http://18.220.183.110/api/doc)

### Getting an Authentication Token
#### **`POST`** **api/signup**
Hitting the endpoint with the following request body would register a user with this email. This endpoint can be used only once with the same username and email. Check **`POST`** **api/api-token-auth** to retrieve a registered user's auth token.

Request Body:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```
Example **HTTP 200** Response:
```json
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
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```
Example **HTTP 200** Response:
```json
{
  "token": "string"
}
```
This `token` can be used as the `bearer` token in the http `authorization` header to authenticate some non-public endpoints.
### Search
#### **`POST`** **api/images/full-text-search**
Request Body:
```json
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
```json
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
#### **`POST`** **api/images/full-text-search**


### Local Installation Guidelines
The project is fully dockerized, so it is very easy to start up the required containers from the docker-compose.yml file in the project root.
```
docker-compose up --build
```
However, This project requires some cloud resources like (AWS S3 file storage) in order to function properly. So, in order to run the project locally you need to have **.debug.env** file in the project root which should look like the following:
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


#### TODO
- mention image resizing example somewhere
- return better results for the image search & upload image task result
- maybe add an api endpoint for resizing images