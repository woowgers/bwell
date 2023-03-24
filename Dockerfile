FROM python:3.10-alpine

WORKDIR /app

RUN apk update && \
    apk add gcc &&\
    addgroup python &&\
    adduser -SG python python &&\
    chown -R python:python /app

ENV PATH="/home/python/.local/bin:$PATH"

USER python

COPY --chown=python:python ./src/ ./
COPY --chown=python:python ./requirements.txt ./requirements.txt
COPY --chown=python:python ./bin/ ./bin/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

