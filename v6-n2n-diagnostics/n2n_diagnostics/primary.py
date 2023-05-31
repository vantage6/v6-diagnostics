""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""
import socket
from typing import Any, Dict, Tuple

from vantage6.client import ContainerClient
from vantage6.tools.util import info
from time import sleep
import traceback

MESSAGE = b'Hello Python\n'
ECHO_TASK = 'echo'
WAIT = 5
TIMEOUT = 20
ENDLESS_SLEEP = 10000
WAIT_TASK = 'wait'
RETRY = 20


def echo(client, data, other_nodes, **kwargs):
    try:
        return try_echo(client, other_nodes)
    except Exception as e:
        info('Exception!')
        info(traceback.format_exc())
        raise e


def try_echo(client: ContainerClient, other_nodes):
    # ids = get_secondary_organizations(client, exclude_orgs)
    # The input fot the algorithm is the same for all organizations
    # in this case
    info("Defining input parameters")
    # create a new task for all organizations in the collaboration.
    info(f"Dispatching node-tasks to organizations {other_nodes}")
    task = client.create_new_task(input_={'method': ECHO_TASK}, organization_ids=other_nodes)
    info(f'Waiting {WAIT} seconds for the algorithm containers to boot up...')

    # Ip address and port of algorithm can be found in results model
    num_nodes = len(other_nodes)
    addresses = _await_port_numbers(client, task.get('id'), num_nodes=num_nodes)
    succeeded_echos = []
    info(f'Echoing to {len(addresses)} algorithms...')

    for a in addresses:
        ip = a['ip']
        port = a['port']
        info(f'Sending message to {ip}:{port}')

        try:
            succeeded_echos.append(_check_echo(ip, port))
        except socket.timeout:
            info('Timeout! Skipping to next address.')

    info(f'Succeeded echos: {succeeded_echos}')
    return succeeded_echos


def _await_port_numbers(client: ContainerClient, task_id, num_nodes):
    result_objects = client.get_algorithm_addresses(task_id=task_id)
    c = 0
    while len(result_objects) < num_nodes:
        if c >= RETRY:
            info('Cannot contact all organizations!')
            break

        info('Polling results for port numbers...')
        result_objects = client.get_algorithm_addresses(task_id=task_id)
        info(str(result_objects))
        c += 1
        sleep(4)

    return result_objects


def _get_available_addresses(result_objects) -> Tuple[int, str]:
    for r in result_objects:
        ip, port = _get_address_from_result(r)
        if port:
            yield ip, port


def get_secondary_organizations(client, exclude_orgs):
    organizations = client.get_organizations_in_my_collaboration()
    info(str(exclude_orgs))
    ids = [organization.get('id') for organization in organizations]
    if exclude_orgs:
        ids = [i for i in ids if i not in exclude_orgs]
    return ids


def _get_address_from_result(result: Dict[str, Any]) -> Tuple[str, int]:
    address = result['ip']
    port = result['port']

    return address, port


def _check_echo(host, port):
    info(f'Checking echo on {host}:{port}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        s.connect((host, port))
        s.sendall(MESSAGE)
        response = s.recv(len(MESSAGE))
        return response == MESSAGE
