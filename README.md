<h1 align="center">
  <br>
  <a href="https://vantage6.ai"><img src="https://github.com/IKNL/guidelines/blob/master/resources/logos/vantage6.png?raw=true" alt="vantage6" width="400"></a>
</h1>

<h3 align=center> An open source infrastructure for privacy enhancing analysis</h3>

--------------------

# v6-diagnostics

This algorithm is part of the [vantage6](https://vantage6.ai) solution. This repository contains diagnostic tools for debugging and testing the vantage6 infrastructure on a high level.

## Running the algorithm

The diagnostics are typically run via the vantage6 CLI against a development network:

```bash
v6 test feature-test
```

A full feature test may run a **data extraction** step (`read_csv`), the **central** `base_features` function. See [usage.rst](docs/v6-diagnostics/usage.rst) for details.

The ``v6 test integration-test`` command and ``v6 test feature-test`` command will run this algorithm.

## Build

```bash
make image
```

## Install (development)

```bash
git clone https://github.com/vantage6/v6-diagnostics.git
cd v6-diagnostics
uv sync --group dev
```

## LICENCE

Apache License 2.0

See the [vantage6 documentation](https://docs.vantage6.ai/) for detailed instructions on how to install and use the server and nodes.

------------------------------------
> [vantage6](https://vantage6.ai)
