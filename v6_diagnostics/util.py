
import traceback
from typing import Any


class DiagnosticResult:
    """Class to store the results of a diagnostic test."""

    def __init__(self, name: str, success: bool, payload: Any = None,
                 exception: Exception = None) -> None:
        self.name = name
        self.success = success
        self.payload = payload
        self.exception = exception
        self.traceback = traceback.format_exc() if exception else None

    @property
    def json(self):
        """Return a JSON representation of the result."""
        return {
            'name': self.name,
            'success': self.success,
            'payload': str(self.payload),
            'exception': str(self.exception),
            'traceback': self.traceback
        }

    def __str__(self):
        return f'{self.name}: {self.success}'

    def __repr__(self):
        return str(self)


def header(text):
    """Print header."""
    print('\n' + text.center(80, '-'))