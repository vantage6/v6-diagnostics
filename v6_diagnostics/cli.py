# Note that the pickle module is no longer supported in vantage6 v4+.
import pickle
import click
import sys

from typing import Any

from rich.console import Console
from rich.table import Table

from vantage6.client import UserClient
from vantage6.tools.util import info, warn, error


class DiagnosticRunner:

    def __init__(self, client: UserClient, collaboration_id: int,
                 organizations: int | str, online_only: bool = False):

        self.client = client
        self.collaboration_id = collaboration_id
        info(organizations)
        info(online_only)

        if isinstance(organizations, str):
            col = self.client.collaboration.get(self.collaboration_id)
            self.organization_ids = [org['id'] for org in col['organizations']]
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
        return self.vpn_features()

    def base_features(self) -> None:
        task = self.client.task.create(
            collaboration=self.collaboration_id,
            name="test",
            description="Basic Diagnostic test",
            image="harbor2.vantage6.ai/algorithms/diagnostic",
            input={
                "master": True,
                "method": "base_features",
            },
            organizations=self.organization_ids,
        )

        result = self.client.wait_for_results(task_id=task.get("id"))
        print("\n")
        for res in result:
            self.display_diagnostic_results(res)

    def vpn_features(self) -> None:

        self.client.node.list(collaboration=self.collaboration_id)

        task = self.client.task.create(
            collaboration=self.collaboration_id,
            name="test",
            description="VPN Diagnostic test",
            image="harbor2.vantage6.ai/algorithms/diagnostic",
            input={
                "master": True,
                "method": "vpn_features",
                "kwargs": {"other_nodes": self.organization_ids}
            },
            organizations=self.organization_ids,
        )

        result = self.client.wait_for_results(task_id=task.get("id"))
        print("\n")
        for res in result:
            self.display_diagnostic_results(res)

    def display_diagnostic_results(self, result: dict) -> None:
        res = pickle.loads(result["result"])
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

        return res


@click.command(name="feature-tester")
@click.option("--host", type=str, default="http://localhost")
@click.option("--port", type=int, default=5000)
@click.option("--path", type=str, default="")
@click.option("--username", type=str, default="root")
@click.option("--password", type=str, default="root")
@click.option("--collaboration", type=int, default=1)
@click.option("-o", "--organization", type=int, default=[], multiple=True)
@click.option("--all-nodes", is_flag=True)
@click.option("--online-only", is_flag=True)
def feature_tester(
    host: str, port: int, path: str, username: str, password: str,
    collaboration: int, organization: list[int | str], all_nodes: bool,
    online_only: bool
) -> list[dict]:

    if all_nodes and organization:
        error("Cannot use --all and --organization at the same time.")
        sys.exit(1)

    if all_nodes or not organization:
        organization = 'all'

    client = UserClient(host=host, port=port, path=path, log_level='critical')
    client.authenticate(username=username, password=password)
    client.setup_encryption(None)
    diagnose = DiagnosticRunner(client, collaboration, organization,
                                online_only)
    res = diagnose(base=False)
    return res


if __name__ == '__main__':

    # check number of arguments
    if len(sys.argv) != 6:
        print("Usage: python cli.py <host> <port> <path> <username> "
              "<password>")
        sys.exit(1)

    (host, port, path, username, password) = sys.argv[1:]
    client = UserClient(host=host, port=port, path=path)

    client.authenticate(username=username, password=password)
    client.setup_encryption(None)

    diagnose = DiagnosticRunner(client)

    res = diagnose(base=False)
