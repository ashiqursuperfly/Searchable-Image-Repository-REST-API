FROM nginx:latest

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY uwsgi_params /etc/nginx/uwsgi_params

USER root

# setup self-signed ssl
RUN mkdir /etc/nginx/ssl
RUN chmod 700 /etc/nginx/ssl
COPY ssl-debug.crt /etc/nginx/ssl
COPY ssl-debug.key /etc/nginx/ssl

# setup static dirs
RUN mkdir -p /vol/static
RUN chmod 755 /vol/static

# USER nginx
