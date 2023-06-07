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

TODO: check that the temporary volume is readable and writable by the
      child algorithm container.
TODO: child container should trigger different function
"""
import os
import requests
import jwt
import base64
import json

from pathlib import Path

from requests.exceptions import ConnectionError
from vantage6.client.algorithm_client import AlgorithmClient

from v6_diagnostics.util import DiagnosticResult, header


def diagnose_environment():
    """Diagnose the environment of the algorithm container."""
    header('Diagnose the environment of the algorithm container')
    # print(f'ENVIRONMENT: {os.environ}')
    return DiagnosticResult('ENVIRONMENT', True, os.environ)


def diagnose_input_file():
    """Diagnose the input file."""
    header('Diagnose the input file')
    try:
        with open(os.environ['INPUT_FILE'], 'rb') as f:
            input_ = f.read()
        return DiagnosticResult('INPUT_FILE', True, input_)
    except Exception as e:
        return DiagnosticResult('INPUT_FILE', False, exception=e)


def diagnose_output_file():
    """Diagnose the output file."""
    header('Diagnose the output file')
    test_word = 'test'
    try:
        with open(os.environ['OUTPUT_FILE'], 'w') as f:
            f.write(test_word)

        with open(os.environ['OUTPUT_FILE'], 'r') as f:
            success = f.read() == test_word

        return DiagnosticResult('OUTPUT_FILE', success)
    except Exception as e:
        return DiagnosticResult('OUTPUT_FILE', False, exception=e)


def diagnose_token_file():
    """Diagnose the token file."""
    header('Diagnose the token file')
    try:
        with open(os.environ['TOKEN_FILE'], 'r') as f:
            token = f.read()
        return DiagnosticResult('TOKEN_FILE', True, token)
    except Exception as e:
        return DiagnosticResult('TOKEN_FILE', False, exception=e)


def diagnose_temporary_volume():
    """Diagnose the temporary volume."""
    header('Diagnose writing to temporary volume')
    try:
        temp_file = Path(os.environ["TEMPORARY_FOLDER"]) / 'test.txt'
        with open(temp_file, 'w') as f:
            f.write('test')
        return DiagnosticResult('TEMPORARY_VOLUME', True)
    except Exception as e:
        return DiagnosticResult('TEMPORARY_VOLUME', False, exception=e)


def diagnose_temporary_volume_file_exists():
    """Diagnose the temporary volume."""
    header('Diagnose that the temporary file is created')
    try:
        temp_file = Path(os.environ["TEMPORARY_FOLDER"]) / 'test.txt'
        file_exists = Path(temp_file).exists()
        return DiagnosticResult('TEMPORARY_VOLUME_FILE_EXISTS', file_exists)
    except Exception as e:
        return DiagnosticResult('TEMPORARY_VOLUME_FILE_EXISTS', False,
                                exception=e)


def diagnose_local_proxy():
    """Diagnose the local proxy."""
    header('Diagnose the local proxy')
    try:
        host = os.environ['HOST']
        port = os.environ['PORT']
        response = requests.get(f'{host}:{port}/version')
        return DiagnosticResult('LOCAL_PROXY', response.status_code == 200)
    except Exception as e:
        return DiagnosticResult('LOCAL_PROXY', False, exception=e)


def diagnose_local_proxy_subtask():
    """Diagnose the local proxy."""
    header('Diagnose the local proxy subtask')
    try:
        host = os.environ['HOST']
        port = os.environ['PORT']

        with open(os.environ['TOKEN_FILE'], 'r') as f:
            token = f.read()

        identity = (
            jwt.decode(token, options={"verify_signature": False})['sub']
        )

        client = AlgorithmClient(host, port, token)
        input_ = base64.b64encode(
            json.dumps({
                'method': 'diagnose_local_proxy_subtask_stop'
            })
        ).decode('utf-8')
        task = client.task.create(
            name='feature-tester-subtask',
            description='This task is from the feature tester',
            organization_ids=[identity.get('organization_id')],
            input_=input_
        )
        result = client.wait_for_result(task_id=task.get('id'))

        return DiagnosticResult('CREATE_SUBTASK', bool(result.get('data')))
    except Exception as e:
        return DiagnosticResult('CREATE_SUBTASK', False, exception=e)


def diagnose_local_proxy_subtask_stop():
    """Subtask stop"""
    return True


def diagnose_isolation():
    header('Diagnose the isolation of the algorithm container')
    try:
        requests.get('https://google.nl')
    except ConnectionError:
        return DiagnosticResult('ISOLATION', True)
    except Exception as e:
        return DiagnosticResult('ISOLATION', False, exception=e)
    return DiagnosticResult('ISOLATION', False)


def diagnose_external_port():
    """Diagnose the external port."""
    header('Diagnose the external port')
    try:
        with open(os.environ['TOKEN_FILE'], 'r') as f:
            token = f.read()

        host = os.environ['HOST']
        port = os.environ['PORT']

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
        print('debug')
        print(result)
        print(f'--> Found {len(result["addresses"])} port(s)')
        for addr in result['addresses']:
            if addr['label'] == 'port5':
                print(f'--> found "port5": {addr["port"]}')
                p5 = True
            elif addr['label'] == 'port8':
                print(f'--> found "port8":{addr["port"]}')
                p8 = True
            else:
                print('--> Found an unexpected port!')
                pU = False

        return DiagnosticResult('EXTERNAL_PORT_TEST', all([p5, p8, pU]),
                                payload=result)
    except Exception as e:
        return DiagnosticResult('EXTERNAL_PORT_TEST', False, exception=e)


def diagnose_database():
    """Diagnose the file based database."""
    header('Diagnose the file based database')
    try:
        db_uri = os.environ['DATABASE_URI']
        db_path = Path(db_uri.replace('sqlite:///', ''))
        if db_path.exists():
            return DiagnosticResult('DATABASE', True, payload=db_path)
        else:
            return DiagnosticResult('DATABASE', False, payload=db_path)
    except Exception as e:
        return DiagnosticResult('DATABASE', False, exception=e)
