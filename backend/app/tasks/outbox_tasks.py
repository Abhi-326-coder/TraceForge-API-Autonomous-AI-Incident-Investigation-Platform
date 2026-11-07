from celery import shared_task

from app.services.outbox_dispatcher_service import (
    dispatch_pending_events,
)


@shared_task(
    name="dispatch_outbox_events",
    max_retries=3,
)
def dispatch_outbox_events():

    try:
        return dispatch_pending_events(batch_size=20)

    except Exception as exc:
        raise dispatch_outbox_events.retry(
            exc=exc,
            countdown=10,
        )