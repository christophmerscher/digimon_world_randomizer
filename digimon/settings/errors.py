"""Exception hierarchy for settings parsing + validation failures."""

from __future__ import annotations


class SettingsError(Exception):
    """Base exception for settings problems that can be shown directly
    to the user.
    """


class SettingsJsonError(SettingsError):
    """Settings string was not valid JSON."""

    def __init__(self, error) -> None:
        super().__init__("Failed to parse JSON")
        self.error = error


class SettingsValidationError(SettingsError):
    """Settings JSON parsed successfully but did not match the expected shape."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(_format_errors(errors))


def _format_errors(errors: list[str]) -> str:
    out = "Settings validation failed:"
    for error in errors:
        out += "\n - " + error
    return out
