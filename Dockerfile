# basic python3 image as base
FROM continuumio/miniconda3

# This is a placeholder that should be overloaded by invoking
# docker build with '--build-arg PKG_NAME=...'
ARG PKG_NAME="v6_diagnostics"
ENV PKG_NAME=${PKG_NAME}

ENV PATH="/opt/conda/envs/py310/bin/:${PATH}"


EXPOSE 8888
LABEL p8888="port8"

EXPOSE 5555
LABEL p5555="port5"

# install federated algorithm
COPY . /app

RUN apt update

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
RUN dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb

RUN conda create -n py310 python=3.10

RUN pip install /app



# Tell docker to execute `docker_wrapper()` when the image is run.
CMD python -c "from vantage6.algorithm.tools.wrap import wrap_algorithm; wrap_algorithm()"