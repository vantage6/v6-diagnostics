"""
This script is used to test the basic features of the algorithm container. It
does not use any wrapper functions. The following features are tested:

    Environment variables
        Reports the environment variables that are set in the algorithm
        container by the node instance. For example the location of the input,
        token and output files.
    Input file
        Reports the contents of the input file. You can verify that the input
        set by the client is actually received by the algorithm.
    Output file
        Writes 'test' to the output file and reads it back.
    Token file
        Prints the contents of the token file. It should contain a JWT that you
        can decode and verify the payload. The payload contains information
        like the organization and collaboration ids.
    Temporary directory
        Creates a file in the temporary directory. The temporary directory is
        a directory that is shared between all containers that share the same
        run id. This checks that the temporary directory is writable.
    Local proxy
        Sends a request to the local proxy. The local proxy is used to reach
        the central server from the algorithm container. This is needed as
        parent containers need to be able to create child containers
        (=subtasks). The local proxy also handles encryption/decryption of the
        input and results as the algorithm container is not allowed to know
        the private key.
    Subtask creation
        Creates a subtask (using the local proxy) and waits for the result.
    Isolation test
        Checks if the algorithm container is isolated such that it can not
        reach the internet. It tests this by trying to reach google.nl, so make
        sure this is not a whitelisted domain when testing.
    Database readable
        Check if the file-based database is readable.
"""

# TODO: check that the temporary volume is readable and writable by the
#       child algorithm container.
# TODO: child container should trigger different function
import os
from pathlib import Path

import jwt
import pandas as pd
import requests
from requests.exceptions import ConnectionError

from vantage6.common.globals import (
    DATAFRAME_BETWEEN_GROUPS_SEPARATOR,
    DATAFRAME_WITHIN_GROUP_SEPARATOR,
)

from vantage6.algorithm.client import AlgorithmClient
from vantage6.algorithm.decorator.action import federated
from vantage6.algorithm.tools.util import get_env_var

from v6_diagnostics.util import DiagnosticResult, header


def diagnose_environment() -> DiagnosticResult:
    """Diagnose the environment of the algorithm container."""
    header("Diagnose the environment of the algorithm container")
    diagnostic = DiagnosticResult("ENVIRONMENT", True, os.environ)
    print(diagnostic)
    return diagnostic


def diagnose_input_file() -> DiagnosticResult:
    """Diagnose the input file."""
    header("Diagnose the input file")
    try:
        with open(get_env_var("INPUT_FILE"), "rb") as f:
            input_ = f.read()
        diagnostic = DiagnosticResult("INPUT_FILE", True, input_)
    except Exception as exc:
        diagnostic = DiagnosticResult("INPUT_FILE", False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_output_file() -> DiagnosticResult:
    """Diagnose the output file."""
    header("Diagnose the output file")
    test_word = "test"
    try:
        with open(get_env_var("OUTPUT_FILE"), "w") as f:
            f.write(test_word)

        with open(get_env_var("OUTPUT_FILE"), "r") as f:
            success = f.read() == test_word

        diagnostic = DiagnosticResult("OUTPUT_FILE", success)
    except Exception as exc:
        diagnostic = DiagnosticResult("OUTPUT_FILE", False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_token() -> DiagnosticResult:
    """Diagnose the token file."""
    header("Diagnose the token file")
    try:
        token = get_env_var("CONTAINER_TOKEN")
        diagnostic = DiagnosticResult("CONTAINER_TOKEN", True, token)
    except Exception as exc:
        diagnostic = DiagnosticResult("CONTAINER_TOKEN", False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_local_proxy() -> DiagnosticResult:
    """Diagnose the local proxy."""
    header("Diagnose the local proxy")
    try:
        host = get_env_var("HOST")
        port = get_env_var("PORT")
        response = requests.get(f"{host}:{port}/version")
        diagnostic = DiagnosticResult("LOCAL_PROXY", response.status_code == 200)
    except Exception as exc:
        diagnostic = DiagnosticResult("LOCAL_PROXY", False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_local_proxy_subtask(client: AlgorithmClient) -> DiagnosticResult:
    """Diagnose the local proxy."""
    header("Diagnose the local proxy subtask")
    try:
        token = get_env_var("CONTAINER_TOKEN")

        identity = jwt.decode(token, options={"verify_signature": False})["sub"]

        task = client.task.create(
            method="diagnose_local_proxy_subtask_stop",
            name="feature-tester-subtask",
            description="This task is from the feature tester",
            organizations=[identity.get("organization_id")],
        )

        result = client.wait_for_results(task.get("id"))

        diagnostic = DiagnosticResult("CREATE_SUBTASK", result)
    except Exception as exc:
        diagnostic = DiagnosticResult("CREATE_SUBTASK", False, exception=exc)

    print(diagnostic)
    return diagnostic


@federated
def diagnose_local_proxy_subtask_stop(*_args, **_kwargs) -> bool:
    """Subtask stop"""
    return True


def diagnose_isolation() -> DiagnosticResult:
    header("Diagnose the isolation of the algorithm container")
    try:
        requests.get("https://google.com")
    except ConnectionError:
        diagnostic = DiagnosticResult("ISOLATION", True)
        print(diagnostic)
        return diagnostic
    except Exception as exc:
        # We could end up here by some other error. This does not necessary
        # mean that the algorithm is not isolated.
        diagnostic = DiagnosticResult("ISOLATION", False, exception=exc)
        print(diagnostic)
        return diagnostic

    # If we get here, we have a connection to the internet
    diagnostic = DiagnosticResult("ISOLATION", False)
    print(diagnostic)
    return diagnostic


def diagnose_session_folder() -> DiagnosticResult:
    """Diagnose that the session folder is writable."""
    header("Diagnose the session folder")
    test_word = "test"
    try:
        session_folder = Path(get_env_var("SESSION_FOLDER"))
        session_folder.mkdir(parents=True, exist_ok=True)
        test_file = session_folder / "v6_diagnostics_test.txt"
        test_file.write_text(test_word, encoding="utf-8")
        success = test_file.read_text(encoding="utf-8") == test_word
        diagnostic = DiagnosticResult("SESSION_FOLDER", success)
    except Exception as exc:
        diagnostic = DiagnosticResult("SESSION_FOLDER", False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_dataframe_readable() -> DiagnosticResult:
    """Verify that requested session dataframe(s) can be read from disk."""
    header("Diagnose session dataframe readability")
    try:
        dfs = get_env_var("USER_REQUESTED_DATAFRAMES")
        if not dfs:
            raise ValueError("No session dataframes were requested for this task")

        session_folder = Path(get_env_var("SESSION_FOLDER"))
        labels = dfs.split(DATAFRAME_BETWEEN_GROUPS_SEPARATOR)[0].split(
            DATAFRAME_WITHIN_GROUP_SEPARATOR
        )
        readable = []
        for label in labels:
            df = pd.read_parquet(session_folder / f"{label}.parquet")
            readable.append({"label": label, "shape": df.shape})

        diagnostic = DiagnosticResult("DATAFRAME_READABLE", True, readable)
    except Exception as exc:
        diagnostic = DiagnosticResult("DATAFRAME_READABLE", False, exception=exc)

    print(diagnostic)
    return diagnostic


# TODO it would be nice to extend this check to see if the database is the correct one.
# That is probably best/easiest when we have specific checks for a federated step.
def diagnose_database() -> DiagnosticResult:
    """Diagnose the database."""
    header("Diagnose the database")
    try:
        requested_dataframes = get_env_var("USER_REQUESTED_DATAFRAMES")
        diagnostic = DiagnosticResult("DATAFRAME ENV VARS", True, requested_dataframes)
    except Exception as exc:
        diagnostic = DiagnosticResult("DATAFRAME ENV VARS", False, exception=exc)

    print(diagnostic)
    return diagnostic
