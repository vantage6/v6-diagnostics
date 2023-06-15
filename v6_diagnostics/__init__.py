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
    diagnose_local_proxy_subtask_stop,  # child task runs this
    diagnose_isolation,
    diagnose_external_port,
    diagnose_database
)


def main(client, *args, **kwargs):
    base = base_features()
    vpn = vpn_features()
    return base + vpn


def base_features() -> list[DiagnosticResult]:
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
        diagnose_local_proxy_subtask().json,
        diagnose_isolation().json,
        diagnose_external_port().json,
        diagnose_database().json
    ]

    print(results)

    return results


def vpn_features() -> list[DiagnosticResult]:
    return []
