### builder stage

# pull official base image
FROM python:3.8-slim as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#### final stage

# pull official base image
FROM python:3.8-slim

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN adduser --system app --group

# TZ data
ARG TZ='America/Argentina/Buenos_Aires'
ENV DEFAULT_TZ ${TZ}

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/cash_flow
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# update alpine packages
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata locales libgl1-mesa-dev libglib2.0-0 libgtk2.0-dev

# configure timezone
RUN cp /usr/share/zoneinfo/${DEFAULT_TZ} /etc/localtime && apt-get purge -y tzdata && rm -rf /var/lib/apt/lists/*

# configure locale
RUN sed -i '/es_AR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG es_AR.UTF-8
ENV LANGUAGE es_AR:es
ENV LC_ALL es_AR.UTF-8

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $HOME

# change to the app user
USER app
