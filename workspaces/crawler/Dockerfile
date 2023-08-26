ARG SERVICE=crawler
ARG PORT=0
ARG VERBOSE=INFO

FROM ms-base:latest AS builder

# Generate requirements and install *all* dependencies.
COPY pyproject.toml poetry.lock /

RUN poetry export --dev --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt
RUN pip install --prefix=/bin --force-reinstall -r requirements.txt

FROM python:slim-buster AS runtime

ENV SERVICE=${SERVICE} \
    PORT=${PORT} \
    VERBOSE=${VERBOSE}

# copy in our built poetry + venv
COPY --from=builder /bin /usr/local

RUN mkdir /usr/src/${SERVICE}\
    # Create the system account and give permissions
    && groupadd -r ${SERVICE} \ 
    # add the user to the folder, and add a name for the system group and the group
    && useradd -d /usr/src -r -g ${SERVICE} ${SERVICE} \
    # add the rights to the folder and its sub-folders
    && chown ${SERVICE}:${SERVICE} -R /usr/src

WORKDIR /usr/src/${SERVICE}

COPY --chown=${SERVICE}:${SERVICE} ${SERVICE}/ .
USER ${SERVICE}
WORKDIR /usr/src

CMD [ "python", "-m", "${SERVICE}" ]