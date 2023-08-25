import click
import sys

from vantage6.client import UserClient
from vantage6.algorithm.tools.util import error

from cli.diagnostic_runner import DiagnosticRunner

@click.command(name="feature-tester")
@click.option("--host", type=str, default="http://localhost",
              help="URL of the server")
@click.option("--port", type=int, default=5000, help="Port of the server")
@click.option("--api-path", type=str, default="/api",
              help="API path of the server")
@click.option("--username", type=str, default="root",
              help="Username of vantage6 user account to create the task with")
@click.option("--password", type=str, default="root",
              help="Password of vantage6 user account to create the task with")
@click.option("--collaboration", type=int, default=1,
              help="ID of the collaboration to create the task in")
@click.option("-o", "--organization", type=int, default=[], multiple=True,
              help="ID(s) of the organization(s) to create the task for")
@click.option("--all-nodes", is_flag=True,
              help="Run the diagnostic test on all nodes in the collaboration")
@click.option("--online-only", is_flag=True,
              help="Run the diagnostic test on only nodes that are online")
def feature_tester(
    host: str, port: int, api_path: str, username: str, password: str,
    collaboration: int, organization: list[int | str], all_nodes: bool,
    online_only: bool
) -> list[dict]:
    """
    Run diagnostic checks on a vantage6 network.

    This command will create a task in the requested collaboration that will
    test the functionality of vantage6, and will report back the results.
    """
    if all_nodes and organization:
        error("Cannot use --all and --organization at the same time.")
        sys.exit(1)

    if all_nodes or not organization:
        organization = 'all'

    client = UserClient(host=host, port=port, path=api_path,
                        log_level='critical')
    client.authenticate(username=username, password=password)
    client.setup_encryption(None)
    diagnose = DiagnosticRunner(client, collaboration, organization,
                                online_only)
    res = diagnose(base=False)
    return res
