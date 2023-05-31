<h1 align="center">
  <br>
  <a href="https://vantage6.ai"><img src="https://github.com/IKNL/guidelines/blob/master/resources/logos/vantage6.png?raw=true" alt="vantage6" width="400"></a>
</h1>

<h3 align=center> A privacy preserving federated learning solution</h3>

--------------------

# v6-n2n-diagnostics
This algorithm is part of the [vantage6](https://vantage6.ai) solution. Vantage6 allows to 
execute computations on federated datasets. This repository provides a boilerplate for new algorithms.

# How to use
This vantage6 algorithm includes a handy client class that helps you run its methods as a 
vantage6 user.

```python
from vantage6.client import v6client

client = v6client.Client(YOUR_V6_HOST, YOUR_V6_PORT, verbose=True)

client.authenticate(YOUR_USERNAME, YOUR_PASSWORD)
client.setup_encryption(YOUR_PRIVATE_KEY)


n2nclient = N2NDiagnosticsClient(client)

# Master node should be the organization id of the node that you want to run the primary 
# algorithm on
# Other nodes should be the nodes in the collaboration that you want the master_node to connect to.
task = n2nclient.echo(master_node, collaboration_id, other_nodes)
```

## Read more
See the [documentation](https://docs.vantage6.ai/) for detailed instructions on how to install and use the server and nodes.

------------------------------------
> [vantage6](https://vantage6.ai)
