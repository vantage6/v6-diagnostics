ARG BASE=5.0
FROM ghcr.io/vantage6/infrastructure/algorithm-base:${BASE}

ARG PKG_NAME="v6_diagnostics"

# install federated algorithm
COPY . /app
RUN uv pip install --system -e /app

ENV PKG_NAME=${PKG_NAME}

# Tell docker to execute `wrap_algorithm()` when the image is run. This function
# will ensure that the algorithm method is called properly.
CMD python -c "from vantage6.algorithm.tools.wrap import wrap_algorithm; wrap_algorithm()"
