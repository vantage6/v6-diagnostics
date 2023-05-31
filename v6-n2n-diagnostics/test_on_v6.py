#!/usr/bin/env python3

from time import sleep

import clize
import vantage6.client as v6client

from n2n_diagnostics.client import N2NDiagnosticsClient

RETRY = 50
SLEEP = 10
ECHO = 'echo'
WAIT = 'wait'
TEST_IMAGE = 'harbor2.vantage6.ai/algorithms/n2n-diagnostics'


def test_on_v6(host: str, port: int, username: str, password: str, collaboration_id: int, *,
               private_key: str = None, method: str = ECHO, image: str = TEST_IMAGE,
               tag: str = 'latest'):
    client = v6client.Client(host, port, verbose=True)

    client.authenticate(username, password)
    client.setup_encryption(private_key)

    # Get organizations
    active_nodes = client.node.list(is_online=True)
    active_nodes = active_nodes['data']

    print(active_nodes)

    org_ids = [n['organization']['id'] for n in active_nodes]

    print(f' Active nodes{org_ids}')
    master_node = org_ids[0]
    other_nodes = org_ids[0:]

    n2nclient = N2NDiagnosticsClient(client, image=image, tag=tag)

    task = None

    if method == ECHO:
        task = n2nclient.echo(master_node, collaboration_id, other_nodes)
    elif method == WAIT:
        task = n2nclient.wait(org_ids, collaboration_id)

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
