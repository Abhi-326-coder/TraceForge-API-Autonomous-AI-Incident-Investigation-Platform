import threading
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.investigation_state_service import (
    heartbeat_investigation,
)


class WorkerHeartbeat:

    def __init__(
        self,
        investigation_id: int,
        worker_id: str,
        interval_seconds: int = 30,
    ):
        self.investigation_id = investigation_id
        self.worker_id = worker_id
        self.interval_seconds = interval_seconds

        self.stop_event = threading.Event()
        self.lost_lease = threading.Event()

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

    def start(self):
        self.thread.start()

    def _run(self):
        while not self.stop_event.wait(
            self.interval_seconds
        ):
            db: Session = SessionLocal()

            try:
                renewed = heartbeat_investigation(
                    db,
                    self.investigation_id,
                    self.worker_id,
                )

                if not renewed:
                    self.lost_lease.set()
                    break

            except Exception:
                self.lost_lease.set()
                break

            finally:
                db.close()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)