# basic python3 image as base
FROM harbor.vantage6.ai/algorithms/algorithm-base

# This is a placeholder that should be overloaded by invoking
# docker build with '--build-arg PKG_NAME=...'
ARG PKG_NAME="v6-feature-tester-py"

# install deps
COPY ./requirements.txt /requirements.txt
RUN pip install -r ./requirements.txt

# install federated algorithm
COPY . /app

ENV PKG_NAME=${PKG_NAME}

# Expose ports to be used by te infrastructure
LABEL p8888="port8"
EXPOSE 8888

LABEL p5050="port5"
EXPOSE 5050

# Tell docker to execute `docker_wrapper()` when the image is run.
CMD python ./app/main.py