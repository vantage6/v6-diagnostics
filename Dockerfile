# basic python3 image as base
FROM continuumio/miniconda3

# This is a placeholder that should be overloaded by invoking
# docker build with '--build-arg PKG_NAME=...'
ARG PKG_NAME="v6_diagnostics"
ENV PKG_NAME=${PKG_NAME}

RUN apt update && apt install -y iproute2 traceroute iputils-ping curl

# install federated algorithm
COPY . /app
RUN pip install /app


EXPOSE 8888
LABEL p8888="port8"

EXPOSE 5555
LABEL p5555="port5"

# Tell docker to execute `docker_wrapper()` when the image is run.
CMD python -c "from vantage6.algorithm.tools.wrap import wrap_algorithm; wrap_algorithm()"