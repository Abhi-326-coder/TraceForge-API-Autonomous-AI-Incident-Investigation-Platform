import pytest

from app.services.audit_service import record_audit_event


def test_records_patch_approval(db_session, user_a):
    event = record_audit_event(
        db_session,
        action="PATCH_APPROVED",
        outcome="SUCCESS",
        actor_user_id=user_a.id,
        resource_type="PatchApproval",
        resource_id=42,
        metadata={"patch_id": 42},
    )

    db_session.commit()
    db_session.refresh(event)

    assert event.action == "PATCH_APPROVED"
    assert event.actor_user_id == user_a.id
    assert event.resource_id == "42"


def test_rejects_unknown_action(db_session):
    with pytest.raises(ValueError):
        record_audit_event(
            db_session,
            action="DELETE_ALL_DATA",
            outcome="SUCCESS",
        )


def test_rejects_secret_like_metadata(db_session):
    with pytest.raises(ValueError):
        record_audit_event(
            db_session,
            action="PATCH_APPROVED",
            outcome="SUCCESS",
            metadata={"access_token": "do-not-log"},
        )


def test_rejects_invalid_outcome(db_session):
    with pytest.raises(ValueError):
        record_audit_event(
            db_session,
            action="PATCH_APPROVED",
            outcome="MAYBE",
        )
