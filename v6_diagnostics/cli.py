import json
import click
import sys

from typing import Any

from rich.console import Console
from rich.table import Table

from vantage6.client import UserClient
from vantage6.algorithm.tools.util import info, error

IMAGE_NAME = "harbor2.vantage6.ai/algorithms/diagnostic"
# TODO remove
IMAGE_NAME = "test-diagnostic"


class DiagnosticRunner:

    def __init__(self, client: UserClient, collaboration_id: int,
                 organizations: int | str, online_only: bool = False):

        self.client = client
        self.collaboration_id = collaboration_id

        if isinstance(organizations, str):
            # col = self.client.collaboration.get(self.collaboration_id)
            # TODO get all organizations if multiple pages
            orgs = self.client.organization.list(
                collaboration=self.collaboration_id
            )
            self.organization_ids = [org['id'] for org in orgs['data']]
        elif isinstance(organizations, list | tuple):
            self.organization_ids = organizations

        if online_only:
            nodes = self.client.node.list(
                collaboration=self.collaboration_id,
                is_online=True, include_metadata=False
            )
            info(nodes)
            online_orgs = [node['organization']['id'] for node in nodes]
            self.organization_ids = \
                list(set(self.organization_ids).intersection(online_orgs))

        info(f"Running diagnostics to {len(self.organization_ids)} "
             "organization(s)")
        info(f"  organizations: {self.organization_ids}")
        info(f"  collaboration: {self.collaboration_id}")

    def __call__(self, base: bool = True, vpn: bool = True,
                 *args: Any, **kwds: Any) -> Any:
        return self.base_features()
        # return self.base_features() | self.vpn_features()

    def base_features(self) -> dict:
        task = self.client.task.create(
            collaboration=self.collaboration_id,
            name="test",
            description="Basic Diagnostic test",
            image=IMAGE_NAME,
            input_={
                "method": "base_features",
            },
            organizations=self.organization_ids,
        )

        result = self.client.wait_for_results(task_id=task.get("id"))
        print("\n")
        for res in result['data']:
            self.display_diagnostic_results(res)

        return result

    def vpn_features(self) -> dict:

        self.client.node.list(collaboration=self.collaboration_id)

        task = self.client.task.create(
            collaboration=self.collaboration_id,
            name="test",
            description="VPN Diagnostic test",
            image=IMAGE_NAME,
            input_={
                "method": "vpn_features",
                "kwargs": {"other_nodes": self.organization_ids}
            },
            organizations=self.organization_ids,
        )

        result = self.client.wait_for_results(task_id=task.get("id"))
        print("\n")
        for res in result['data']:
            self.display_diagnostic_results(res)

        return result

    def display_diagnostic_results(self, result: dict) -> None:
        print("we are here!")
        res = json.loads(result["result"])
        t_ = Table(title="Basic Diagnostics Summary")
        t_.add_column('name')
        t_.add_column('success')
        e_ = Table(title="Basic Diagnostics Errors")
        e_.add_column('name')
        e_.add_column('exception')
        e_.add_column('traceback')
        e_.add_column('payload')
        errors = False
        for diag in res:
            if diag['success']:
                success = ":heavy_check_mark: [green]success[/green]"
            else:
                success = ":x: [red]failed[/red]"
                e_.add_row(diag["name"], diag["exception"], diag["traceback"],
                           diag["payload"])
                errors = True
            t_.add_row(diag["name"], success)

        console = Console()
        console.print(t_)
        if errors:
            console.print(e_)


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
