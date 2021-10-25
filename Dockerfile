FROM python:3.7-alpine
MAINTAINER romulino-travelperk

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN \
 apk add --no-cache postgresql-libs jpeg-dev && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev musl-dev zlib zlib-dev&& \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web

USER user