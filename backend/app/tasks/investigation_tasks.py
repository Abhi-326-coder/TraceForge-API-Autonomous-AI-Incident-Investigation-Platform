from app.worker import celery_app

@celery_app.task(
    bind=True,
    name="traceforge.run_investigation",
    max_retries=2,
    default_retry_delay=10,
)
def run_investigation_task(
    self,
    investigation_id: int,
) -> dict:
    """
    Run one TraceForge investigation in a worker process.

    The workflow implementation is delegated to a service so
    the Celery task remains small.
    """
    from app.services.investigation_worker_service import (
        execute_investigation,
    )
    
    try:
        return execute_investigation(
            investigation_id=investigation_id
        )
    except Exception as exc:
        # Don't retry every failure blindly. A later hardening step
        # will distinguish transient provider errors from permanent
        # workflow or validation errors.
        raise self.retry(exc=exc)