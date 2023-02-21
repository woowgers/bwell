FROM python:3.11-slim-buster

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN apt-get update \
    && apt-get install -qq --no-install-recommends gcc build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/* \
    && groupadd -g ${GID} python \
    && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
    && chown -R python:python /app


ENV PATH="/home/python/.local/bin:$PATH"

USER python

COPY --chown=python:python ./src/ ./
COPY --chown=python:python ./requirements.txt ./requirements.txt
COPY --chown=python:python ./bin/ ./bin/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x ./bin/*

