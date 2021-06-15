FROM python:3.7-slim

# Install poetry
RUN pip install --upgrade --no-cache-dir pip poetry
COPY . /src
WORKDIR /src

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
RUN set -ex \
	&& rm -rf \
        /var/cache/debconf/*-old \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base
