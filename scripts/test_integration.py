"""Run the real services with unique, disposable volumes, and always clean up."""

import os
import subprocess
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
project = f"galene-test-{uuid4().hex[:12]}"
environment = {
    **os.environ,
    "GALENE_IMAGE_TAG": project,
    "GALENE_APP_ENV": "test",
    "GALENE_DATA_DIR": "/unused-by-test-compose",
}
compose = [
    "docker",
    "compose",
    "--env-file",
    "/dev/null",
    "-p",
    project,
    "-f",
    "compose.yaml",
    "-f",
    "compose.test.yaml",
    "--profile",
    "test",
]


def run(
    *args: str, check: bool = True, timeout: int = 600, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*compose, *args],
        cwd=ROOT,
        env=environment,
        text=True,
        check=check,
        timeout=timeout,
        capture_output=capture,
    )


def expect_refusal(service: str, message: str) -> None:
    result = run(
        "run", "--rm", "--no-deps", service, check=False, timeout=30, capture=True
    )
    if result.returncode == 0 or message not in result.stderr:
        raise RuntimeError(
            f"{service} did not refuse as expected: {result.stdout}{result.stderr}"
        )
    print(f"Verified {service} refusal: {message}", flush=True)


def main() -> None:
    try:
        run("build", "migrate", "api", "worker", "frontend", "integration")
        run(
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            "120",
            "api",
            "worker",
            "frontend",
            "nginx",
        )
        run(
            "exec",
            "-T",
            "api",
            "python",
            "-c",
            """
import sqlite3
from pathlib import Path
with sqlite3.connect('/data/db/inventory.sqlite3') as connection:
    connection.execute('CREATE TABLE persistence_probe (value TEXT NOT NULL)')
    connection.execute('INSERT INTO persistence_probe VALUES (?)', ('synthetic persistence check',))
Path('/data/media/probe.txt').write_text('synthetic media check')
""",
        )
        expect_refusal("worker", "A worker already owns this database.")
        run(
            "up",
            "-d",
            "--no-deps",
            "--force-recreate",
            "--wait",
            "--wait-timeout",
            "90",
            "api",
            "worker",
        )
        run("run", "--rm", "--no-deps", "integration")
        # A future database must block both entrypoints even outside Compose ordering.
        run("stop", "api", "worker")
        run(
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "-c",
            """
import sqlite3
with sqlite3.connect('/data/db/inventory.sqlite3') as connection:
    connection.execute("UPDATE alembic_version SET version_num = 'future_revision'")
""",
        )
        for service in ("api", "worker"):
            expect_refusal(service, "Database schema is incompatible.")
        print(
            "Docker integration passed: routing, limits, persistence, worker lock, schema refusal."
        )
    except BaseException:
        run("logs", "--no-color", "--tail", "80", check=False)
        raise
    finally:
        run("down", "--volumes", "--remove-orphans", check=False)


if __name__ == "__main__":
    main()
