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
    External port test
        Check that the algorithm can find its own ports. Algorithms can
        request a dedicated port for communication with other algorithm
        containers. The port that they require is stored in the Dockerfile
        using the ``EXPORT`` and ``LABEL`` keywords. For example:
        ```Dockefile
        LABEL p8888="port8"
        EXPOSE 8888
        ```
        It however does not check that the application is actually listening
        on the port.
    Database readable
        Check if the file-based database is readable.
"""
# TODO: check that the temporary volume is readable and writable by the
#       child algorithm container.
# TODO: child container should trigger different function
import os
import requests
import jwt

from pathlib import Path

from requests.exceptions import ConnectionError
from vantage6.algorithm.client import AlgorithmClient

from v6_diagnostics.util import DiagnosticResult, header, get_env_var


def diagnose_environment() -> DiagnosticResult:
    """Diagnose the environment of the algorithm container."""
    header('Diagnose the environment of the algorithm container')
    diagnostic = DiagnosticResult('ENVIRONMENT', True, os.environ)
    print(diagnostic)
    return diagnostic


def diagnose_input_file() -> DiagnosticResult:
    """Diagnose the input file."""
    header('Diagnose the input file')
    try:
        with open(get_env_var('INPUT_FILE'), 'rb') as f:
            input_ = f.read()
        diagnostic = DiagnosticResult('INPUT_FILE', True, input_)
    except Exception as exc:
        diagnostic = DiagnosticResult('INPUT_FILE', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_output_file() -> DiagnosticResult:
    """Diagnose the output file."""
    header('Diagnose the output file')
    test_word = 'test'
    try:
        with open(get_env_var('OUTPUT_FILE'), 'w') as f:
            f.write(test_word)

        with open(get_env_var('OUTPUT_FILE'), 'r') as f:
            success = f.read() == test_word

        diagnostic = DiagnosticResult('OUTPUT_FILE', success)
    except Exception as exc:
        diagnostic = DiagnosticResult('OUTPUT_FILE', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_token_file() -> DiagnosticResult:
    """Diagnose the token file."""
    header('Diagnose the token file')
    try:
        with open(get_env_var('TOKEN_FILE'), 'r') as f:
            token = f.read()
        diagnostic = DiagnosticResult('TOKEN_FILE', True, token)
    except Exception as exc:
        diagnostic = DiagnosticResult('TOKEN_FILE', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_temporary_volume() -> DiagnosticResult:
    """Diagnose the temporary volume."""
    header('Diagnose writing to temporary volume')
    try:
        temp_file = Path(get_env_var("TEMPORARY_FOLDER")) / 'test.txt'
        with open(temp_file, 'w') as f:
            f.write('test')
        diagnostic = DiagnosticResult('TEMPORARY_VOLUME', True)
    except Exception as exc:
        diagnostic = DiagnosticResult('TEMPORARY_VOLUME', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_temporary_volume_file_exists() -> DiagnosticResult:
    """Diagnose the temporary volume."""
    header('Diagnose that the temporary file is created')
    try:
        temp_file = Path(get_env_var("TEMPORARY_FOLDER")) / 'test.txt'
        file_exists = Path(temp_file).exists()
        diagnostic = DiagnosticResult('TEMPORARY_VOLUME_FILE_EXISTS',
                                      file_exists)
    except Exception as exc:
        diagnostic = DiagnosticResult('TEMPORARY_VOLUME_FILE_EXISTS', False,
                                      exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_local_proxy() -> DiagnosticResult:
    """Diagnose the local proxy."""
    header('Diagnose the local proxy')
    try:
        host = get_env_var('HOST')
        port = get_env_var('PORT')
        response = requests.get(f'{host}:{port}/version')
        diagnostic = DiagnosticResult('LOCAL_PROXY',
                                      response.status_code == 200)
    except Exception as exc:
        diagnostic = DiagnosticResult('LOCAL_PROXY', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_local_proxy_subtask(client: AlgorithmClient) -> DiagnosticResult:
    """Diagnose the local proxy."""
    header('Diagnose the local proxy subtask')
    try:

        with open(get_env_var('TOKEN_FILE'), 'r') as f:
            token = f.read()

        identity = (
            jwt.decode(token, options={"verify_signature": False})['sub']
        )

        input_ = {
            'master': True,
            'method': 'diagnose_local_proxy_subtask_stop'
        }

        task = client.task.create(
            name='feature-tester-subtask',
            description='This task is from the feature tester',
            organizations=[identity.get('organization_id')],
            input_=input_
        )

        result = client.wait_for_results(task.get('id'))

        diagnostic = DiagnosticResult('CREATE_SUBTASK', result)
    except Exception as exc:
        diagnostic = DiagnosticResult('CREATE_SUBTASK', False, exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_local_proxy_subtask_stop(*_args, **_kwargs) -> bool:
    """Subtask stop"""
    return True


def diagnose_isolation() -> DiagnosticResult:
    header('Diagnose the isolation of the algorithm container')
    try:
        requests.get('https://google.nl')
    except ConnectionError:
        diagnostic = DiagnosticResult('ISOLATION', True)
        print(diagnostic)
        return diagnostic
    except Exception as exc:
        # We could end up here by some other error. This does not necessary
        # mean that the algorithm is not isolated.
        diagnostic = DiagnosticResult('ISOLATION', False, exception=exc)
        print(diagnostic)
        return diagnostic

    # If we get here, we have a connection to the internet
    diagnostic = DiagnosticResult('ISOLATION', False)
    print(diagnostic)
    return diagnostic


def diagnose_external_port() -> DiagnosticResult:
    """Diagnose the external port."""
    header('Diagnose the external port')
    try:
        with open(get_env_var('TOKEN_FILE'), 'r') as f:
            token = f.read()

        host = get_env_var('HOST')
        port = get_env_var('PORT')

        # port should be published as we are running this code.. So no
        # need for polling
        response = requests.get(
            f'{host}:{port}/vpn/algorithm/addresses',
            headers={'Authorization': 'Bearer ' + token},
            params={'include_parent': True, 'include_children': True}
        )

        # we also assume that only a single task has been posted as we
        # are not testing the connectivity between nodes yet
        p5 = p8 = False
        pU = True
        result = response.json()
        for addr in result['addresses']:
            if addr['label'] == 'port5':
                p5 = True
            elif addr['label'] == 'port8':
                p8 = True
            else:
                pU = False

        diagnostic = DiagnosticResult('EXTERNAL_PORT_TEST', all([p5, p8, pU]),
                                      payload=result)
    except Exception as exc:
        diagnostic = DiagnosticResult('EXTERNAL_PORT_TEST', False,
                                      exception=exc)

    print(diagnostic)
    return diagnostic


def diagnose_database() -> list[DiagnosticResult]:
    """Diagnose the file-based database."""
    header('Diagnose the file-based database')
    diagnostics = []
    try:
        db_labels = get_env_var('DB_LABELS').split(',')
        for label in db_labels:
            db_uri = get_env_var(f'{label.upper()}_DATABASE_URI')
            db_type = get_env_var(f'{label.upper()}_DATABASE_TYPE')

            if db_type in ['sql', 'omop', 'sparql']:
                # We do not expect these databases to be files, so don't
                # perform checks on them
                continue
            elif Path(db_uri).exists():
                diagnostic = DiagnosticResult(
                    f'DATABASE {label.upper()}', True
                )
            else:
                diagnostic = DiagnosticResult(
                    f'DATABASE {label.upper()}', False,
                    payload=f"{db_uri} does not exist"
                )
            diagnostics.append(diagnostic)
    except Exception as exc:
        diagnostic = DiagnosticResult('DATABASE', False, exception=exc)
        diagnostics.append(diagnostic)

    for diagnostic in diagnostics:
        print(diagnostic)
    return diagnostics
