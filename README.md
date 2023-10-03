<h1 align="center">
  <br>
  <a href="https://vantage6.ai"><img src="https://github.com/IKNL/guidelines/blob/master/resources/logos/vantage6.png?raw=true" alt="vantage6" width="400"></a>
</h1>

<h3 align=center> An open source infrastructure for privacy enhancing analysis</h3>

--------------------

# v6-diagnostics
This algorithm is part of the [vantage6](https://vantage6.ai) solution. This repository contains diagnostic tools for debugging and testing the vantage6 infrastructure on a high level.

## Usage
### Install
```bash
git clone https://github.com/vantage6/v6-diagnostics.git
cd v6-diagnostic
pip install .
```

### Execute
```bash
vtest --host http://localhost --port 5000 --username *** --password *** \
    --collaboration 1 [--online-only] [--organization 1] [--organization N]
```

```bash
python -i v6_diagnostic/cli.py [host] [port] [path] [username] [password]
```

````python
>>> from vantage6.client import Client
>>> client = Client('http://localhost', 5000, '***', '***')
>>> from v6_diagnostics.cli import DiagnosticRunner
>>> runner = DiagnosticRunner(client, collaboration_id, organizations,
...                           online_only)
>>> runner()
````

## Build

### Package
```bash
python setup.py sdist bdist_wheel
```

### Docker image
```bash
# build the docker image
make image

# push the docker image to the registry
make push

# build and push the docker image
make publish
```

## LICENCE
Apache License 2.0

## Read more
See the [documentation](https://docs.vantage6.ai/) for detailed instructions on how to install and use the server and nodes.

------------------------------------
> [vantage6](https://vantage6.ai)
