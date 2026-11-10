from collections.abc import Mapping
from typing import Any


def present_workflow(
    *, workflow: str, context: Mapping[str, Any]
) -> str:
    """Present a named triage or routing workflow to a modeled user."""
    raise NotImplementedError
