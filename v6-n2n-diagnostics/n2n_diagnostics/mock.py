"""
Mock module that will provide placeholders for actual api calls to the vantage6 that aren't
available yet.
"""

MOCK_IP = '127.0.0.1'
MOCK_PORT = 9999
TASK_ID = 1
RESULT_ID = 2


def get_algorithm_address(result):
    """
    Retrieve the address of the algorithm container associated with the given result.
    """

    return f'{MOCK_IP}:{MOCK_PORT}'


def create_new_task(organization_ids):
    # secondary.RPC_echo(None)

    return {'id': TASK_ID}


def get_results(task_id):
    return [{'id': RESULT_ID, 'port': MOCK_PORT}]


def get_node_address(result):
    return MOCK_IP
