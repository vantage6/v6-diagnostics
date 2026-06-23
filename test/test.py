"""
Run pytest to test v6-diagnostics locally.

    uv sync --group dev
    uv run pytest test/test.py -v
"""

import importlib

import pandas as pd
from requests.exceptions import ConnectionError

from vantage6.algorithm.mock.network import MockNetwork

bf = importlib.import_module("v6_diagnostics.base_features")

DATABASE_LABEL = "Database"


def test_diagnose_local_proxy_subtask_stop():
    """Federated subtask should return True."""
    network = MockNetwork(
        datasets=[{DATABASE_LABEL: {"database": pd.DataFrame({"a": [1]})}}],
        module_name="v6_diagnostics",
    )
    client = network.user_client
    org_ids = [org["id"] for org in client.organization.list()]

    task = client.task.create(
        method="diagnose_local_proxy_subtask_stop",
        arguments={},
        organizations=[org_ids[0]],
    )
    results = client.wait_for_results(task.get("id"))
    assert results[0] is True


def test_diagnose_environment():
    result = bf.diagnose_environment()
    assert result.success is True
    assert result.name == "ENVIRONMENT"


def test_diagnose_input_file(tmp_path, monkeypatch):
    input_file = tmp_path / "input.json"
    input_file.write_bytes(b'{"test": true}')
    monkeypatch.setenv("INPUT_FILE", str(input_file))

    result = bf.diagnose_input_file()
    assert result.success is True


def test_diagnose_output_file(tmp_path, monkeypatch):
    output_file = tmp_path / "output.json"
    monkeypatch.setenv("OUTPUT_FILE", str(output_file))

    result = bf.diagnose_output_file()
    assert result.success is True
    assert output_file.read_text() == "test"


def test_diagnose_token(monkeypatch):
    monkeypatch.setenv("CONTAINER_TOKEN", "test-token")

    result = bf.diagnose_token()
    assert result.success is True
    assert result.payload == "test-token"


def test_diagnose_local_proxy(monkeypatch):
    monkeypatch.setenv("HOST", "http://localhost")
    monkeypatch.setenv("PORT", "5000")

    class MockResponse:
        status_code = 200

    monkeypatch.setattr(
        bf.requests,
        "get",
        lambda *_args, **_kwargs: MockResponse(),
    )

    result = bf.diagnose_local_proxy()
    assert result.success is True


def test_diagnose_isolation_blocks_connection(monkeypatch):
    def raise_connection_error(*_args, **_kwargs):
        raise ConnectionError("blocked")

    monkeypatch.setattr(bf.requests, "get", raise_connection_error)

    result = bf.diagnose_isolation()
    assert result.success is True


def test_diagnose_isolation_fails_when_reachable(monkeypatch):
    class MockResponse:
        status_code = 200

    monkeypatch.setattr(
        bf.requests,
        "get",
        lambda *_args, **_kwargs: MockResponse(),
    )

    result = bf.diagnose_isolation()
    assert result.success is False


def test_diagnose_session_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSION_FOLDER", str(tmp_path))

    result = bf.diagnose_session_folder()
    assert result.success is True
    assert (tmp_path / "v6_diagnostics_test.txt").exists()


def test_diagnose_database(monkeypatch):
    monkeypatch.setenv(
        "USER_REQUESTED_DATAFRAMES",
        '[{"type": "dataframe", "dataframe_id": 1}]',
    )

    result = bf.diagnose_database()
    assert result.success is True
