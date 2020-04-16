FROM python:3.8-alpine

MAINTAINER Danfishel Private Ltd

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /userMservice
WORKDIR /userservice
COPY ./userMservice /userservice

RUN adduser -D user
USER user

