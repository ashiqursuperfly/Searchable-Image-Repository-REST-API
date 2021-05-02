FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/scripts:${PATH}"

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
# packages required for setting up WSGI
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libc-dev python3-dev default-libmysqlclient-dev

RUN pip install -r /requirements.txt
# RUN service rabbitmq-server start

RUN mkdir /app
COPY ./src /app
WORKDIR /app
COPY ./scripts /scripts

RUN chmod +x /scripts/*

# folder to serve media files by nginx
RUN mkdir -p /vol/web/media
# folder to serve static files by nginx
RUN mkdir -p /vol/web/static

# always good to run our src with a different user other than root user
RUN useradd user
RUN chown -R user:user /vol
# chmod 755 means read and execute access to the user and write access to the owner
RUN chmod -R 755 /vol/web
RUN chown -R user:user /app
RUN chmod -R 755 /app
# switch to our user
USER user

CMD ["entrypoint.sh"]


