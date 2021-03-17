
# --> Check environment variables
# The environment is set by the node and can be extended by using
# the `algorithm_envs` key in the configuration file of the node.
import os
print(os.environ)

# --> Check that we can read the input, output and token file
with open(os.environ['INPUT_FILE'], 'r') as f:
    print('--> Reading input file')
    print(f'INPUT FILE: {f.read()}')

with open(os.environ['OUTPUT_FILE'], 'w') as f:
    print('--> Writing to output file (contents: test)')
    f.write('test')

with open(os.environ['OUTPUT_FILE'], 'r') as f:
    print('--> Reading output file back and check')
    print(f.read())

with open(os.environ['TOKEN_FILE'], 'r') as f:
    print('--> Reading token file')
    print(f'TOKEN: {f.read()}')

# --> Check that we can write to the temporary volume
temp_file = f'{os.environ["TEMPORARY_FOLDER"]}/test.txt'
with open(temp_file, 'w') as f:
    print(f'--> Writing to temporary file: {temp_file}')
    f.write('test')

print('--> Test that the temporary file is created')
from pathlib import Path
file_exists = Path(temp_file).exists()
print(f'FILE CREATED: {file_exists}')

# --> Check that we can reach the local proxy
print('--> Test that we can reach the local proxy (and thereby the server)')
import requests
host = os.environ['HOST']
port = os.environ['PORT']
requests.get(f'{host}:{port}/version')

# --> check that we cannot reach another address
print('--> Verify that the container has no internet connection')
response = requests.get('https://google.nl')
passed = response.status_code != 200
print(f'ISOLATED: {passed}')

# --> Check if you can reach services in the network.
import requests
