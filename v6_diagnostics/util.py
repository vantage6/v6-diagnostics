import traceback
from typing import Any
import os
import base64

from vantage6.common.globals import STRING_ENCODING, ENV_VAR_EQUALS_REPLACEMENT


class DiagnosticResult:
    """Class to store the results of a diagnostic test."""

    def __init__(
        self, name: str, success: bool, payload: Any = None, exception: Exception = None
    ) -> None:
        self.name = name
        self.success = success
        self.payload = payload
        self.exception = exception
        self.traceback = traceback.format_exc() if exception else None

    @property
    def json(self):
        """Return a JSON representation of the result."""
        return {
            "name": self.name,
            "success": self.success,
            "payload": str(self.payload),
            "exception": str(self.exception),
            "traceback": self.traceback,
        }

    def __str__(self):
        return f"{self.name}: {self.success}"

    def __repr__(self):
        return str(self)


def header(text):
    """Print header."""
    print("\n" + text.center(80, "-"))


# def get_env_var(var_name: str, default: str | None = None) -> str:
#     """
#     Get the value of an environment variable. Environment variables are encoded
#     by the node so they need to be decoded here.

#     Note that this decoding follows the reverse of the encoding in the node:
#     first replace '=' back and then decode the base32 string.

#     Parameters
#     ----------
#     var_name : str
#         Name of the environment variable

#     Returns
#     -------
#     var_value : str | None
#         Value of the environment variable, or default value if not found
#     """
#     try:
#         encoded_env_var_value = \
#             os.environ[var_name].replace(
#                 ENV_VAR_EQUALS_REPLACEMENT, "="
#             ).encode(STRING_ENCODING)
#         return base64.b32decode(encoded_env_var_value).decode(STRING_ENCODING)
#     except KeyError:
#         return default
