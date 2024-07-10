FROM ubuntu:20.04

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .