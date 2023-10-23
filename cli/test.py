import click
import sys

from vantage6.client import UserClient
from vantage6.algorithm.tools.util import error
from vantage6.cli.dev import create, start, stop, remove
from vantage6.cli.utils import prompt_config_name, check_config_name_allowed

from cli.diagnostic_runner import DiagnosticRunner

@click.group(name="test")
def cli_test() -> None:
    """
    The `vtest` commands allow you to run diagnostic tests on your vantage6
    environment.
    """

@cli_test.command(name="run-test-algorithm")
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
    Run diagnostic checks on an existing vantage6 network.

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


@cli_test.command(name="run-integration-test")
@click.option('-n', '--name', default=None, type=str,
              help="Name for your development setup")
@click.option('--server-url', type=str, default='http://host.docker.internal',
              help='Server URL to point to. If you are using Docker Desktop, '
              'the default http://host.docker.internal should not be changed.')
@click.option('-i', '--image', type=str, default=None,
              help='Server Docker image to use')
@click.pass_context
def run_integration_test(click_ctx: click.Context, name: str, server_url: str,
                         image: str) -> list[dict]:
    """
    Create development network and run diagnostic checks on it.

    This is a full integration test of the vantage6 network. It will create
    a test server with some nodes using the `vdev` commands, and then run the
    v6-diagnostics algorithm to test all functionality.
    """
    # get name for the development setup - if not given - and check if it is
    # allowed
    name = prompt_config_name(name)
    check_config_name_allowed(name)

    # create server & node configurations and create test resources (
    # collaborations, organizations, etc)
    click_ctx.invoke(
        create_demo_network, name=name, num_nodes=3, server_url=server_url,
        server_port=5000, image=image
    )

    # start the server and nodes
    click_ctx.invoke(
        start_demo_network, name=name, system_folders=True, server_image=image,
        node_image=image
    )

    # run the diagnostic tests
    # TODO the username and password should be coordinated with the vdev
    # command
    diagnose_results = click_ctx.invoke(
        feature_tester, host="http://localhost", port=5000, api_path='/api',
        username='org_1-admin', password='password', collaboration=1,
        organization=[], all_nodes=True, online_only=False
    )

    # clean up the test resources
    click_ctx.invoke(stop_demo_network, name=name, system_folders=True)
    click_ctx.invoke(remove_demo_network, name=name, system_folders=True)

    return diagnose_results
