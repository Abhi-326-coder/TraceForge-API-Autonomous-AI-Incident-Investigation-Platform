import pytest
from fastapi import HTTPException

from app.services.authorization_service import get_owned_project


def test_user_cannot_access_another_users_project(
    db_session,
    user_a,
    user_b,
    project_a,
):
    project_a.owner_id = user_a.id
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        get_owned_project(
            db_session,
            project_a.id,
            user_b,
        )

    assert exc.value.status_code == 404