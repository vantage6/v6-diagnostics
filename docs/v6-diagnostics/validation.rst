Validation
==========

Unit and smoke tests
--------------------

Install dev dependencies and run pytest:

.. code-block:: bash

    uv sync --group dev
    uv run pytest test/test.py -v

The tests use ``MockNetwork`` for federated smoke tests and ``monkeypatch`` for
environment-dependent central checks (input/output files, token, proxy, isolation,
session folder).

Integration test
----------------

The primary end-to-end validation is the vantage6 CLI against a running dev
network:

.. code-block:: bash

    v6 test feature-test

See the `vantage6 documentation <https://docs.vantage6.ai/>`_ for setup
instructions.
