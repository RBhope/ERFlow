from modules import ForbiddenError
from modules.data_store import DataStore


def authorize(user_id: str, action: str, store: DataStore) -> None:
    role = store.get_role(user_id)

    if action == "save_assessment" and role == "Triage Nurse":
        return

    raise ForbiddenError("This user is not authorized for this action.")