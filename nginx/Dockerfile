FROM nginx:1.22.1

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY index.html /usr/share/nginx/html/


RUN mkdir -p /vol/static && \
    chmod 755 /vol/static

VOLUME /vol/static