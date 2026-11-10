from erflow.modules.data_store import RecordStore


def authorize(
    *, actor_id: str, actor_role: str, action: str, store: RecordStore
) -> None:
    """Check whether the modeled actor may perform a role-specific action."""
    raise NotImplementedError
