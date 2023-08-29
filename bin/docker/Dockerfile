# Copyright 2023 Ricardo Yaben
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM python:slim-buster AS base

FROM base AS builder

# Environment variables for the container
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install dependencies in this image
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev

FROM builder AS release
LABEL maintainer="rmyl@dtu.dk"

ARG PROJECT
ENV PROJECT=$PROJECT

WORKDIR /usr/src/$PROJECT

# Copy the necessary files for the project
COPY pyproject.toml pyproject.toml
COPY lib/ lib/
COPY config/ config/
COPY workspaces/$PROJECT/ workspaces/$PROJECT/

# Configure poetry and install the dependencies
RUN python -m pip install -e workspaces/$PROJECT

ENTRYPOINT ["python", "-m"]