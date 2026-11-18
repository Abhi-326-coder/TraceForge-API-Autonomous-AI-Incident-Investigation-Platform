import hashlib
import json

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Evidence
from app.services.investigation_execution_context import InvestigationExecution
from app.services.investigation_state_service import (
    require_active_investigation_lease,
)


def evidence_idempotency_key(
    investigation_id: int,
    source_type: str,
    provider: str,
    source_reference: str | None,
) -> str | None:
    """Build a stable key only when an explicit source identity exists."""
    if source_reference is None or not source_reference.strip():
        return None

    identity = json.dumps(
        [investigation_id, source_type, provider, source_reference],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def find_evidence_by_source(
    db: Session,
    investigation_id: int,
    source_type: str,
    provider: str,
    source_reference: str | None,
    execution: InvestigationExecution | None = None,
) -> Evidence | None:
    """Look up an existing logical source before repeating node work."""
    if source_reference is None or not source_reference.strip():
        return None
    if execution is not None:
        if execution.investigation_id != investigation_id:
            raise ValueError("Evidence investigation does not match its execution lease.")
        require_active_investigation_lease(
            db,
            investigation_id,
            execution.worker_id,
            execution.lease_token,
        )

    key = evidence_idempotency_key(
        investigation_id,
        source_type,
        provider,
        source_reference,
    )
    evidence = db.execute(
        select(Evidence)
        .where(
            or_(
                Evidence.idempotency_key == key,
                and_(
                    Evidence.idempotency_key.is_(None),
                    Evidence.investigation_id == investigation_id,
                    Evidence.source_type == source_type,
                    Evidence.provider == provider,
                    Evidence.source_reference == source_reference,
                ),
            )
        )
        .order_by(Evidence.id.asc())
        .limit(1)
        .with_for_update()
    ).scalars().first()
    # Release the lease row lock before the caller continues with a provider
    # request; writes revalidate and lock again in create_evidence.
    if execution is not None:
        if evidence is not None:
            db.expunge(evidence)
        db.commit()
    return evidence


def create_evidence(
    db: Session,
    investigation_id: int,
    source_type: str,
    provider: str,
    title: str,
    content: str,
    source_reference: str | None = None,
    execution: InvestigationExecution | None = None,
) -> Evidence:
    if execution is not None:
        if execution.investigation_id != investigation_id:
            raise ValueError("Evidence investigation does not match its execution lease.")
        require_active_investigation_lease(
            db,
            investigation_id,
            execution.worker_id,
            execution.lease_token,
        )

    key = evidence_idempotency_key(
        investigation_id,
        source_type,
        provider,
        source_reference,
    )

    try:
        existing = None
        if key is not None:
            existing = db.execute(
                select(Evidence)
                .where(Evidence.idempotency_key == key)
                .with_for_update()
            ).scalars().first()

            # Adopt pre-migration records on first replay. The identity uses
            # explicit source metadata, never title/content similarity.
            if existing is None:
                existing = db.execute(
                    select(Evidence)
                    .where(
                        Evidence.investigation_id == investigation_id,
                        Evidence.source_type == source_type,
                        Evidence.provider == provider,
                        Evidence.source_reference == source_reference,
                        Evidence.idempotency_key.is_(None),
                    )
                    .order_by(Evidence.id.asc())
                    .limit(1)
                    .with_for_update()
                ).scalars().first()
                if existing is not None:
                    existing.idempotency_key = key
                    db.commit()
                    db.refresh(existing)
                    return existing

            if existing is not None:
                db.commit()
                return existing

        evidence = Evidence(
            investigation_id=investigation_id,
            source_type=source_type,
            provider=provider,
            title=title,
            content=content,
            source_reference=source_reference,
            idempotency_key=key,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence
    except IntegrityError:
        db.rollback()
        if key is None:
            raise
        # A concurrent writer with the same stable source identity committed
        # first. Reuse its row instead of surfacing a duplicate insert.
        existing = db.execute(
            select(Evidence).where(Evidence.idempotency_key == key)
        ).scalars().first()
        if existing is None:
            raise
        return existing
    except Exception:
        db.rollback()
        raise
