# basic python3 image as base
FROM continuumio/miniconda3

# This is a placeholder that should be overloaded by invoking
# docker build with '--build-arg PKG_NAME=...'
ARG PKG_NAME="v6_diagnostics"

RUN apt update && apt install -y iproute2 traceroute iputils-ping curl

# install federated algorithm
COPY ./algorithms/v6-diagnostics/ /app
RUN pip install /app

# TODO remove this later on! and update the COPY line above
COPY ./vantage6-main /vantage6
RUN pip install /vantage6/vantage6-common
RUN pip install /vantage6/vantage6-client
RUN pip install /vantage6/vantage6-algorithm-tools

ENV PKG_NAME=${PKG_NAME}

EXPOSE 8888
LABEL p8888="port8"

EXPOSE 5555
LABEL p5555="port5"

# Tell docker to execute `docker_wrapper()` when the image is run.
CMD python -c "from vantage6.algorithm.tools.wrap import wrap_algorithm; wrap_algorithm('${PKG_NAME}')"