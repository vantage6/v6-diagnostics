from vantage6.client.algorithm_client import AlgorithmClient

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
    diagnose_external_port,
    diagnose_database
)

from v6_diagnostics.vpn import (  # noqa: F401
    diagnose_vpn_connection,
    RPC_echo,
    RPC_wait
)


def base_features(client: AlgorithmClient, *args, **kwargs) \
        -> list[DiagnosticResult]:
    """Run all diagnostics."""
    header('Running base feature diagnostics')
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
        diagnose_external_port().json,
        diagnose_database().json
    ]

    print(results)

    return results


def vpn_features(client: AlgorithmClient, _, other_nodes) \
        -> list[DiagnosticResult]:
    """Run all diagnostics."""
    header('Running VPN feature diagnostics')
    results = [
        diagnose_vpn_connection(client, other_nodes).json
    ]
    return results
