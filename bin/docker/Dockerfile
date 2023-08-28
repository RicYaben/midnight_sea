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
ARG PROJECT

FROM python:slim-buster AS base

FROM base AS builder
LABEL maintainer="rmyl@dtu.dk"

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

RUN mkdir /usr/src/${PROJECT} /usr/src/local \
    # Create the system account and give permissions
    && groupadd -r ${PROJECT} \ 
    # add the user to the folder, and add a name for the system group and the group
    && useradd -d /usr/src -r -g ${PROJECT} ${PROJECT} \
    # add the rights to the folder and its sub-folders
    && chown ${PROJECT}:${PROJECT} -R /usr/src

WORKDIR /usr/src/${PROJECT}

# Copy the necessary files for the project
COPY --chown=${PROJECT}:${PROJECT} pyproject.toml ./
COPY --chown=${PROJECT}:${PROJECT} lib/ lib/
COPY --chown=${PROJECT}:${PROJECT} workspaces/${PROJECT}/ workspaces/${PROJECT}/

# Configure poetry and install the dependencies
RUN python -m install workspaces/${PROJECT}

USER ${PROJECT}
CMD ["python", "-m", "${PROJECT}"]