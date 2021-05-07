## Searchable Image Repository REST API

### Table of Contents
- [Core Features](#core-features)
- [Implementation Details](#implementation-details)
- [API Documentation](#api-documentation)
    - [Getting an authentication token](#getting-an-authtoken)
    - [Categories](#image-category)
    - [Upload](#image-upload)
        - [Single Image Upload](#single-image-upload)
        - [Bulk Image Upload](#bulk-image-upload)
    - [Search](#search)
        - [Full Text Search](#full-text-search)
        - [Image Search](#image-search)
    - [My Images](#my-images)
        - [Fetch My Images](#fetch-my-images)
        - [Delete my Image](#delete-my-image)
    - [Error Handling](#error-handling)
- [Local Installation Guidelines](#local-installation-guidelines)


#### Core Features
- handles single and bulk image uploads with minimal response time
- url based image manipulation to resize images on the fly
- two kinds of image searching is available.
    - i. **Full Text Search** (user enters some keywords or a phrase or a country location)
    - ii. **Image Search** (user enters an image, optionally can also enter full text search parameters that aid narrow down the search space)
- access protection, users can only delete images uploaded by him/her


#### Implementation Details
- built using [**`Django Rest Framework`**](https://www.django-rest-framework.org/)
- uses [**`RabbitMQ`**](https://www.rabbitmq.com/)** as message broker and **[Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html)** as synchronous task queue to carry out long tasks, resulting in minimal response time for bulk image upload
- uses [**`PostgreSQL Full Text Search`**](https://www.postgresql.org/docs/13/textsearch.html) to perform full text search of images based on image meta  
- extracts [**`ORB`**](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html) descriptors from images and uses open cv based matcher for image search
- images are stored in **AWS S3** storage
- images are served through **AWS Cloudfront CDN**
- **URL based Image Manipulation** is available through an **AWS Lambda** function
- served through **nginx** on an **AWS EC2** instance


#### API Documentation


#### Local Installation Guidelines
The project is fully dockerized, so it is very easy to start up the required containers from the docker-compose.yml file in the project root.
```
docker-compose up --build
```
However, This project requires some cloud resources like (AWS S3 file storage) in order to function properly. So, in order to run the project locally you need to have **.debug.env** file in the project root which should look like the following:
```
DEBUG=1
DJANGO_APP_SECRET_KEY=****
AWS_ACCESS_KEY_ID=****
AWS_SECRET_ACCESS_KEY=****
AWS_S3_REGION_NAME=****
AWS_STORAGE_BUCKET_NAME=****
AWS_CLOUDFRONT_DOMAIN=****
ALLOWED_HOSTS=127.0.0.1,localhost
RABBITMQ_DEFAULT_USER=****
RABBITMQ_DEFAULT_PASS=****
POSTGRES_USER=****
POSTGRES_PASSWORD=****
POSTGRES_DB=****
```
