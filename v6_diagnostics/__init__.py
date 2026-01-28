from vantage6.algorithm.decorator.algorithm_client import algorithm_client
from vantage6.algorithm.decorator.action import central
from vantage6.algorithm.client import AlgorithmClient

# use default infra implementation of read_csv
from vantage6.algorithm.data_extraction import read_csv  # noqa: F401

from v6_diagnostics.util import header, DiagnosticResult
from v6_diagnostics.base_features import (  # noqa: F401
    diagnose_environment,
    diagnose_input_file,
    diagnose_output_file,
    diagnose_token_file,
    diagnose_temporary_volume,
    diagnose_temporary_volume_file_exists,
    diagnose_local_proxy,
    diagnose_local_proxy_subtask,
    # child task runs this, so we need to keep the import here
    diagnose_local_proxy_subtask_stop,
    diagnose_isolation,
    diagnose_database,
)


@central
@algorithm_client
def base_features(client: AlgorithmClient) -> list[DiagnosticResult]:
    """
    Run all tests for the base features of vantage6.

    Parameters
    ----------
    client : AlgorithmClient
        The client to use for the diagnostics.

    Returns
    -------
    list[DiagnosticResult]
        The results of the diagnostics.
    """
    header("Running base feature diagnostics")
    results = [
        diagnose_environment().json,
        diagnose_input_file().json,
        diagnose_output_file().json,
        diagnose_token_file().json,
        diagnose_temporary_volume().json,
        diagnose_temporary_volume_file_exists().json,
        diagnose_local_proxy().json,
        diagnose_local_proxy_subtask(client).json,
        diagnose_isolation().json,
    ]
    results.extend([diagnosis.json for diagnosis in diagnose_database()])

    return results
