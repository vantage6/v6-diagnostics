# Note that the pickle module is no longer supported in vantage6 v4+.
import pickle
from typing import Any

from rich.console import Console
from rich.table import Table

from vantage6.client import UserClient


class DiagnosticRunner:

    def __init__(self, client: UserClient):
        self.client = client

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.base_features()

    def base_features(self) -> None:
        task = client.task.create(
            collaboration=1,
            name="test",
            description="Diagnostic test",
            image="harbor2.vantage6.ai/algorithms/diagnostic",
            input={
                "master": True,
                "method": "main"
            },
            organizations=[1],
        )

        result = client.wait_for_results(task_id=task.get("id"))

        res = pickle.loads(result[0]["result"])
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


if __name__ == '__main__':
    client = UserClient(
        host="https://petronas.vantage6.ai",
        port=443,
        path=""
    )

    client.authenticate(username="***", password="***")
    client.setup_encryption(None)

    diagnose = DiagnosticRunner(client)

    res = diagnose()
