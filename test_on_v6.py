#!/usr/bin/env python3

from pathlib import Path
from time import sleep
from typing import List

import clize
import vantage6.client as v6client

from n2n_diagnostics.client import N2NDiagnosticsClient

IMAGE = 'carrrier-harbor.carrier-mu.src.surf-hosted.nl/carrier/n2n-diagnostics'
RETRY = 10
SLEEP = 10
DEFAULT_METHOD = 'echo'


def test_on_v6(host: str, port: int, username: str, password: str, private_key: str,
               collaboration_id: int, *exclude, method: str = DEFAULT_METHOD):
    client = v6client.Client(host, port, verbose=True)

    client.authenticate(username, password)
    client.setup_encryption(None)

    # Get organizations
    active_nodes = client.node.list(is_online=True)
    active_nodes = active_nodes['data']

    org_ids = [n['organization']['id'] for n in active_nodes]

    print(org_ids)
    master_node = org_ids[0]
    other_nodes = org_ids[1:]

    n2nclient = N2NDiagnosticsClient(client, IMAGE)
    task = n2nclient.echo(master_node, collaboration_id, other_nodes)

    print(task)

    result = {}
    for i in range(RETRY):

        for r in task['results']:
            result = client.result.get(r['id'])

            print(result)
            print('Result:')
            print(get_output(result))
            print()
            print('Log:')
            print(get_log(result))

        sleep(SLEEP)
        if result['finished_at']:
            break


def get_output(result):
    return result['result']


def get_log(result):
    return result['log']


if __name__ == '__main__':
    clize.run(test_on_v6)
