# MAKE: sudo docker build -t hovr:0.1 .
#  vlc -vvv rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/2 --sout="#file{dst=/hovr_data/1.mp4}" --no-sout-all --sout-keep --rtsp-tcp
FROM python:3.6

LABEL company="dtec.pro" \
      maintainer="Denis Muratov xeronm@gmail.com" \
      example="docker run --name hovr -it --rm --user hovr hovr:0.1" \
      description="Home Video Recorder (based on VLC)" \
      com.name="hovr" \
      com.version="0.1" \
      com.release-date="2018-12-31"

RUN addgroup hovr && \
    adduser --home /var/hovr --ingroup hovr hovr && \
    mkdir -p /hovr_data && \
    chown hovr:hovr /hovr_data && \
    apt-get update && \
    apt-get install -y vlc && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'django>=2.0' \
        djangorestframework \
        django-compressor \ 
        psycopg2 psycopg2-binary \
        python-vlc requests

WORKDIR /var/hovr

COPY . .
 
ENV DJANGO_SETTINGS_MODULE="config.settings" \
    DJANGO_AUTOMIGRATE="yes" \
    DJANGO_DBINIT="./example/dbinit.json" \
    DJANGO_CONFIG_DATABASES_default_ENGINE="django.db.backends.postgresql" \
    DJANGO_CONFIG_DATABASES_default_NAME="django" \
    DJANGO_CONFIG_DATABASES_default_USER="django" \
    DJANGO_CONFIG_DATABASES_default_PASSWORD="django" \
    DJANGO_CONFIG_DATABASES_default_HOST="db" \
    DJANGO_CONFIG_DATABASES_default_PORT="5432" \
    DJANGO_CONFIG_STATIC__ROOT="/srv/django/public/static" 

VOLUME [ "/hovr_data" ]

EXPOSE 8000

ENTRYPOINT [ "/var/hovr/docker-entrypoint.sh" ]

CMD [ "./manage.py", "runserver", "0:8000" ]
