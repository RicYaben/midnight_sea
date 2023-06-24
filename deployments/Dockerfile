FROM python:slim-buster
LABEL maintainer="rmyl@dtu.dk"

ARG SERVICE
ARG PROJECT=ms
ARG PORT=0
ARG VERBOSE=INFO

# Environment variables for the container
ENV SERVICE=${SERVICE} \
    PORT=${PORT} \
    PROJECT=${PROJECT} \
    VERBOSE=${VERBOSE} \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install dependencies in this image
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev

RUN pip install --upgrade pip

# Installing `poetry` package manager:
RUN pip install poetry  && poetry --version

RUN mkdir /usr/src/${PROJECT}_${SERVICE} /usr/src/local\
    # Create the system account and give permissions
    && groupadd -r ${SERVICE} \ 
    # add the user to the folder, and add a name for the system group and the group
    && useradd -d /usr/src -r -g ${SERVICE} ${SERVICE} \
    # add the rights to the folder and its sub-folders
    && chown ${SERVICE}:${SERVICE} -R /usr/src

WORKDIR /usr/src/code

# Copy the files for poetry
COPY --chown=${SERVICE}:${SERVICE} pyproject.${SERVICE}.toml /pyproject.toml
COPY --chown=${SERVICE}:${SERVICE} poetry.${SERVICE}.lock /poetry.lock

RUN poetry config virtualenvs.create false \
    && poetry add platformdirs \
    && poetry install --no-dev --no-interaction --no-ansi \
    && poetry update

WORKDIR /usr/src/${PROJECT}_${SERVICE}

COPY --chown=${SERVICE}:${SERVICE} ${PROJECT}_${SERVICE}/ .

# Change the user to a non-root user:
USER ${SERVICE}
WORKDIR /usr/src
EXPOSE ${PORT}