# [START cloudrun_pubsub_dockerfile]
# [START run_pubsub_dockerfile]

# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.8

# # Install Imagemagick into the container image.
# # For more on system packages review the system packages tutorial.
# # https://cloud.google.com/run/docs/tutorials/system-packages#dockerfile
# RUN set -ex; \
#     apt-get -y update; \
#     apt-get -y install imagemagick; \
#     rm -rf /var/lib/apt/lists/*

#Install tesseract
# RUN apt-get update -qqy && apt-get install -qqy \
#     tesseract-ocr \
#     libtesseract-dev

RUN apt-get update -qqy; \
    apt-get install -qqy --no-install-recommends automake ca-certificates g++ git libtool libleptonica-dev make pkg-config; \
    rm -rf /var/lib/apt/lists/*

# RUN apt-get update -qqy 
# RUN apt-get install -qqy automake ca-certificates g++ git libtool libleptonica-dev make pkg-config
COPY tesseract-master/ ./tesseract-master/
RUN cd tesseract-master && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig
# RUN apt-get install -qqy tesseract-ocr-eng
# RUN export TESSDATA_PREFIX="/usr/local/share/tessdata"
RUN wget -O /usr/local/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

# [END run_pubsub_dockerfile]
# [END cloudrun_pubsub_dockerfile]
