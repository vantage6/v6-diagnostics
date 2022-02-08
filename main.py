import os
import requests
import jwt

from pathlib import Path


test_results = {}

#
#   CHECK ENVIRONMENT VARIALBES
#
print('--> Reading the environment variables')
print(f'ENVIRONMENT: {os.environ}')
test_results['environment'] = os.environ

#
#   CHECK INPUT_FILE
#
try:
    with open(os.environ['INPUT_FILE'], 'r') as f:
        print('--> Reading input file')
        print(f'INPUT FILE: {f.read()}')
    test_results['READ_INPUT_FILE'] = {'Success': True}
except Exception as e:
    print('--> Reading input file failed')
    test_results['READ_INPUT_FILE'] = {'Success': False, 'Exception': e}

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
    print('--> Reading or Writing output file failed')
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
    print('--> Reading token file failed')
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
    print('--> Writing to temporary folder failed')
    test_results['TEMPORARY_VOLUME'] = {'Success': False, 'Exception': e}

print('--> Test that the temporary file is created')
try:
    file_exists = Path(temp_file).exists()
    print(f'FILE CREATED: {file_exists}')
    test_results['TEMPORARY_VOLUME_FILE_EXISTS'] = {'Success': file_exists}
except Exception as e:
    test_results['TEMPORARY_VOLUME_FILE_EXISTS'] = {'Success': False, 'Exception': e}

# --> Check that we can reach the local proxy
print('--> Test that we can reach the local proxy (and thereby the server)')
try:
    host = os.environ['HOST']
    port = os.environ['PORT']
    response = requests.get(f'{host}:{port}/version')
    ok = response.status_code == 200
    test_results['LOCAL_PROXY_CENTRAL_SERVER'] = {'Success': ok}
except Exception as e:
    print('--> Using the local proxy failed')
    test_results['LOCAL_PROXY_CENTRAL_SERVER'] = {'Success': False, 'Exception': e}

# --> check that we cannot reach another address
print('--> Verify that the container has no internet connection')
try:
    try:
        response = requests.get('https://google.nl')
    except ConnectionError:
        test_results['ISOLATION_TEST'] = {'Success': ok}
except Exception as e:
    print('--> Testing an external connection failed...')
    test_results['ISOLATION_TEST'] = {'Success': False, 'Exception': e}

#
# External port test
#
print('--> Check that two ports have been published')
if test_results['READ_TOKEN_FILE']['Success']:
    try:
        # obtain own task id
        id_ = jwt.decode(token, verify=False)['identity'].get('task_id')

        # port should be published as we are running this code.. So no
        # need for polling
        response = requests.get(f'{host}:{port}/task/{id_}/result')

        # we also assume that only a single task has been posted as we
        # are not testing the connectivity between nodes yet
        p5 = p8 = False
        pU = True
        result = response[0]
        print(f'--> Found {len(result["ports"])} port(s)')
        for port in result['ports']:
            if port['label'] =='port5':
                print('--> found \'port5\'')
                p5 = True
            elif port['label'] =='port8':
                print('--> found \'port8\'')
                p8 = True
            else:
                print('--> Found unexpected port!')
                pU = False

        test_results['EXTERNAL_PORT_TEST'] = {'Success': all([p5, p8, pU])}

    except Exception as e:
        print('--> external port check failed')
        test_results['EXTERNAL_PORT_TEST'] = {'Success': False, 'Exception': e}

print(test_results)