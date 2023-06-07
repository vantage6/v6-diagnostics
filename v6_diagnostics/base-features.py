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
        Checks if the algorithm container is isolated such that it can not reach
        the internet. It tests this by trying to reach google.nl, so make sure
        this is not a whitelisted domain when testing.
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
"""
import os
import requests
import jwt
import base64
import pickle

from pathlib import Path
from requests.exceptions import ConnectionError

test_results = {}

#
#   CHECK ENVIRONMENT VARIABLES
#
print('--> Reading the environment variables')
print(f'ENVIRONMENT: {os.environ}')
test_results['environment'] = os.environ

#
#   CHECK INPUT_FILE
#
try:
    with open(os.environ['INPUT_FILE'], 'rb') as f:
        print('--> Reading input file')
        input_ = f.read()
        print(f'INPUT FILE: {input_}')
    test_results['READ_INPUT_FILE'] = {'Success': True}
except Exception as e:
    print('x-> Reading input file failed')
    test_results['READ_INPUT_FILE'] = {'Success': False, 'Exception': e}

#
#  EXIT IF KILLMSG IS RECEIVED
#  this implies that this is a child container
#
killmsg = 'stop'
if pickle.loads(input_) == killmsg:
    print('--> This is a subtask from the feature tester. Exiting.')
    exit(0)

#
#   CHECK OUTPUT FILE
#
try:

    with open(os.environ['OUTPUT_FILE'], 'w') as f:
        print('--> Writing to output file (contents: test)')
        f.write('test')

    with open(os.environ['OUTPUT_FILE'], 'r') as f:
        print('--> Reading output file back and check')
        print(f.read())

    test_results['WRITE_READ_OUTPUT_FILE'] = {'Success': True}
except Exception as e:
    print('x-> Reading or Writing output file failed')
    test_results['WRITE_READ_OUTPUT_FILE'] = {'Success': False, 'Exception': e}

#
#   CHECK TOKEN FILE
#
try:
    with open(os.environ['TOKEN_FILE'], 'r') as f:
        print('--> Reading token file')
        token = f.read()
        print(f'TOKEN: {token}')

    test_results['READ_TOKEN_FILE'] = {'Success': True}
except Exception as e:
    print('x-> Reading token file failed')
    test_results['READ_TOKEN_FILE'] = {'Success': False, 'Exception': e}

#
#   CHECK TEMPORARY VOLUME
#
print('--> Test temporary volume')
try:
    temp_file = f'{os.environ["TEMPORARY_FOLDER"]}/test.txt'
    with open(temp_file, 'w') as f:
        print(f'--> Writing to temporary file: {temp_file}')
        f.write('test')
    test_results['TEMPORARY_VOLUME'] = {'Success': True}
except Exception as e:
    print('x-> Writing to temporary folder failed')
    test_results['TEMPORARY_VOLUME'] = {'Success': False, 'Exception': e}

print('--> Test that the temporary file is created')
try:
    file_exists = Path(temp_file).exists()
    print(f'FILE CREATED: {file_exists}')
    test_results['TEMPORARY_VOLUME_FILE_EXISTS'] = {'Success': file_exists}
except Exception as e:
    print('x-> Test temporary volume failed')
    test_results['TEMPORARY_VOLUME_FILE_EXISTS'] = {
        'Success': False, 'Exception': e
    }

# --> Check that we can reach the local proxy
print('--> Test that we can reach the local proxy (and thereby the server)')
try:
    host = os.environ['HOST']
    port = os.environ['PORT']
    response = requests.get(f'{host}:{port}/version')
    ok = response.status_code == 200
    test_results['LOCAL_PROXY_CENTRAL_SERVER'] = {'Success': ok}
except Exception as e:
    print('x-> Using the local proxy failed')
    test_results['LOCAL_PROXY_CENTRAL_SERVER'] = {
        'Success': False, 'Exception': e
    }

print('--> Test that we can create a subtask')
print('    Depending on the collaboration this test the encryption module')
try:
    host = os.environ['HOST']
    port = os.environ['PORT']

    # obtain collaboration id which is stored in the token
    identity = (jwt.decode(token, options={"verify_signature": False})['sub'])

    response = requests.post(
        f'{host}:{port}/task',
        json={
            'name': 'feature-tester-subtask',
            'description': 'This task is initiated from the feature tester',
            'image': identity.get('image'),
            'collaboration_id': identity.get('collaboration_id'),
            'organizations': [{
                'id': identity.get('organization_id'),
                'input':
                    # do not run any tests
                    base64.b64encode(pickle.dumps(killmsg)).decode('utf-8')
            }],
            'database': 'default'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    test_results['CREATE_SUB_TASK'] = response.json()

except Exception as e:
    print('x-> Using the local proxy to create a task failed')
    test_results['CREATE_SUB_TASK'] = {'Success': False, 'Exception': e}

# --> check that we cannot reach another address
print('--> Verify that the container has no internet connection')
try:
    try:
        response = requests.get('https://google.nl')
    except ConnectionError:
        print('--> Connection error caught')
        # print(e)
        test_results['ISOLATION_TEST'] = {'Success': ok}
except Exception as e:
    print('x-> Testing an external connection failed...')
    test_results['ISOLATION_TEST'] = {'Success': False, 'Exception': e}

#
# External port test
#
print('--> Check that two ports have been published')
if test_results['READ_TOKEN_FILE']['Success']:
    try:
        # obtain own task id
        id_ = (jwt.decode(token, options={"verify_signature": False})['sub'])\
            .get('task_id')

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

        test_results['EXTERNAL_PORT_TEST'] = {'Success': all([p5, p8, pU])}

    except Exception as e:
        print('--> external port check failed')
        test_results['EXTERNAL_PORT_TEST'] = {'Success': False, 'Exception': e}

# Only works for file based databases
print('--> Check attached databases exists')
for key in os.environ:
    if key.endswith('_DATABASE_URI'):
        print(f'--> Found database-path: {key}')
        path_ = os.environ[key]
        if Path(path_).exists():
            print(f'--> database \'{key}\' is reachable: {path_}')
        else:
            print(f'--> database \'{key}\' is *not* reachable: {path_}')

# print to log, so the results can be red
print(test_results)
