""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""

import socket
import asyncio
import traceback

from typing import Any
from time import sleep

from vantage6.algorithm.tools.util import info
from vantage6.algorithm.client import AlgorithmClient

from v6_diagnostics.util import header, DiagnosticResult


MESSAGE = b'Hello vantage6!\n'
WAIT = 5
TIMEOUT = 20
RETRY = 20


def diagnose_vpn_connection(client, other_nodes: list[int], **kwargs) \
        -> DiagnosticResult:
    header('Diagnosing VPN connection')

    try:
        successes = echo(client, other_nodes, **kwargs)
        diagnostic = DiagnosticResult('VPN connection', all(successes),
                                      successes)
    except Exception as e:
        diagnostic = DiagnosticResult('VPN connection', False, exception=e)

    print(diagnostic)
    return diagnostic


def echo(client: AlgorithmClient, other_nodes: list[int], **kwargs) \
        -> list[bool]:
    try:
        return try_echo(client, other_nodes)
    except Exception as exc:
        info('Exception!')
        info(traceback.format_exc())
        raise exc


def try_echo(client: AlgorithmClient, other_nodes: list[int]) -> list[bool]:

    info("Defining input parameters")
    # create a new task for all organizations in the collaboration.
    info(f"Dispatching node-tasks to organizations {other_nodes}")
    subtask = client.task.create(
        input_={"method": "RPC_echo"}, organizations=other_nodes
    )
    info(f"Waiting {WAIT} seconds for the algorithm containers to boot up...")
    sleep(WAIT)

    # Ip address and port of algorithm can be found in results model
    n_nodes = len(other_nodes)
    addresses = _await_port_numbers(client, num_nodes=n_nodes, subtask=subtask["id"])
    succeeded_echos = []
    info(f"Echoing to {len(addresses)} algorithms...")

    for a in addresses:
        ip = a["ip"]
        port = a["port"]
        info(f"Sending message to {ip}:{port}")

        try:
            succeeded_echos.append(_check_echo(ip, port))
        except socket.timeout:
            info("Timeout! Skipping to next address.")

    info(f"Succeeded echos: {succeeded_echos}")
    return succeeded_echos


def _await_port_numbers(
    client: AlgorithmClient, num_nodes: int, subtask: int
) -> list[dict[str, Any]]:

    results = get_vpn_addresses(client, subtask)

    
    info(f"Addresses: {results}")
    attempts = 0
    while len(results) < num_nodes:
        if attempts >= RETRY:
            info("Cannot contact all organizations!")
            break

        info("Polling results for port numbers...")
        results = get_vpn_addresses(client, subtask)
        info(results)
        attempts += 1
        sleep(4)

    info(str(results))
    return results


def get_vpn_addresses(client, subtask):
    results = client.vpn.get_addresses(only_children=True, label="port8")

    return [r for r in results if r["task_id"] == subtask]


def _check_echo(host: str, port: int) -> bool:
    info(f"Checking echo on {host}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        s.connect((host, port))
        s.sendall(MESSAGE)
        response = s.recv(len(MESSAGE))
        return response == MESSAGE


def RPC_echo(*args, **kwargs):
    """
    Start echo socket server
    """
    asyncio.run(_serve_echo())
    return


def RPC_wait(*args, **kwargs):
    try:
        sleep(10000)
    except KeyboardInterrupt:
        pass
    finally:
        return


async def _serve_echo():
    info('Start')
    server = await asyncio.start_server(_handle_echo, '0.0.0.0', 8888)

    info(f'Running echo server for {TIMEOUT} seconds...')

    async with server:
        await asyncio.sleep(TIMEOUT)

    info('Terminated')


async def _handle_echo(reader, writer):
    # Read message
    line = await reader.readline()

    info(f'Received {line.decode()}, will echo')
    writer.writelines([line])
    await writer.drain()

    print('Close the connection')
    writer.close()
