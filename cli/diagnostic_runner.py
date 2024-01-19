import json

from typing import Any
from rich.console import Console
from rich.table import Table

from vantage6.client import UserClient
from vantage6.common import info, debug

IMAGE_NAME = "harbor2.vantage6.ai/algorithms/diagnostic:v4"


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
                is_online=True
            )
            debug(nodes)
            online_orgs = [node['organization']['id'] for node in nodes['data']]
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
            databases=[
                {'label': 'default'}
            ]
        )
        debug(task)

        return self._wait_and_display(task.get("id"))

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

        return self._wait_and_display(task.get("id"))

    def _wait_and_display(self, task_id: int) -> None:
        # TODO should we have the option to combine these in one request? Seems
        # like it would be more efficient
        # TODO ensure that we get all pages of results
        results = self.client.wait_for_results(task_id=task_id)['data']
        runs = self.client.run.from_task(task_id=task_id)['data']
        print("\n")
        for res in results:
            matched_run = [
                run for run in runs if run['id'] == res['run']['id']
            ][0]
            self.display_diagnostic_results(
                res, matched_run['organization']['id']
            )
            print()
        return results

    def display_diagnostic_results(self, result: dict, org_id: int) -> None:
        res = json.loads(result["result"])
        t_ = Table(title=f"Basic Diagnostics Summary (organization {org_id})")
        t_.add_column('name')
        t_.add_column('success')
        e_ = Table(title=f"Basic Diagnostics Errors (organization {org_id})")
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