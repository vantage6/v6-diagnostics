How to use
==========

Overview
--------

The v6-diagnostics algorithm verifies that a vantage6 node can run algorithm
containers correctly. It is typically invoked via ``v6 test feature-test`` against
a development network, not as part of a data-analysis session.

For v5, data-extraction and compute steps are separate. A full feature test runs:

1. **Data extraction** — ``read_csv`` to load a CSV into a session dataframe
2. **Central diagnostics** — ``base_features`` to check environment, I/O, proxy,
   subtasks, isolation, session storage, and session dataframe readability

Functions
---------

``base_features``
^^^^^^^^^^^^^^^^^

Central diagnostics for container infrastructure. When session dataframes are
attached to the task, ``base_features`` also verifies they can be read from the
session folder.

``diagnose_local_proxy_subtask_stop``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Federated subtask used internally by ``base_features`` to verify subtask
creation. Returns ``true``.

``read_csv``
^^^^^^^^^^^^

Data-extraction step (re-exported from vantage6 algorithm tools). Requires a
CSV database URI.

Python client example
---------------------

.. code-block:: python

  from vantage6.client import Client

  server = 'http://localhost'
  port = 5000
  api_path = '/api'
  username = 'root'
  password = 'password'

  client = Client(server, port, api_path)
  client.authenticate(username, password)

  collaboration_id = 1
  org_ids = [org['id'] for org in client.organization.list(collaboration=collaboration_id)]

  # Run central diagnostics (after optional extraction step in a session)
  task = client.task.create(
      collaboration=collaboration_id,
      organizations=[org_ids[0]],
      name='v6-diagnostics',
      description='Infrastructure feature test',
      image='ghcr.io/vantage6/algorithm/diagnostic:latest',
      method='base_features',
      arguments={},
      session=1,
  )
  results = client.wait_for_results(task.get('id'))
