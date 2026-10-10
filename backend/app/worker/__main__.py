import fcntl
import logging
import signal
from threading import Event

from app.adapters.database import create_database, require_current_schema
from app.settings import Settings
from app.worker.health import HEARTBEAT, INTERVAL_SECONDS


def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=logging.INFO, format='{"level":"%(levelname)s","message":"%(message)s"}'
    )
    logging.getLogger("alembic").setLevel(logging.WARNING)
    stop = Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    engine = create_database(settings.database_path)
    try:
        with (settings.storage_dir / "db" / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("A worker already owns this database.") from None
            require_current_schema(engine)
            logging.info("Foundation worker started; no job handlers are registered.")
            try:
                while not stop.is_set():
                    require_current_schema(engine)
                    HEARTBEAT.touch()
                    stop.wait(INTERVAL_SECONDS)
            finally:
                HEARTBEAT.unlink(missing_ok=True)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
