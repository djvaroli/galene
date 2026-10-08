"""Preserve and write Galene session records in the current Git worktree."""

import argparse
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def save_record(history: Path, content: bytes) -> Path:
    """Create and verify a uniquely named historical record."""
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S%fZ-")
    descriptor, name = tempfile.mkstemp(prefix=stamp, suffix=".tmp", dir=history)
    draft = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        if draft.read_bytes() != content:
            raise OSError(f"Record verification failed: {draft}")
        return draft.replace(draft.with_suffix(".md"))
    finally:
        draft.unlink(missing_ok=True)


def write_handoff(root: Path, content: bytes, history_only: bool = False) -> Path:
    """Validate destinations and write a brief or a historical note."""
    root = root.resolve(strict=True)
    brief, history = root / ".HANDOFF", root / ".handoff"
    for path in (brief, history):
        if path.is_symlink():
            raise ValueError(f"Unsafe record destination: {path}")
    if brief.exists() and not brief.is_file():
        raise ValueError(f"Expected an ordinary file: {brief}")
    if history.exists() and not history.is_dir():
        raise ValueError(f"Expected an ordinary directory: {history}")
    tracked = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "--", ".HANDOFF", ".handoff"], text=True
    )
    if tracked:
        raise ValueError("Handoff records are tracked; resolve their destination before writing.")
    history.mkdir(exist_ok=True)
    if not history_only and brief.exists():
        save_record(history, brief.read_bytes())
    record = save_record(history, content)
    if history_only:
        return record
    record.replace(brief)
    return brief


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument(
        "--history", action="store_true", help="Save a note without replacing .HANDOFF"
    )
    arguments = parser.parse_args()
    try:
        root = Path(
            os.fsdecode(
                subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).removesuffix(b"\n")
            )
        )
        result = write_handoff(root, Path(arguments.draft).read_bytes(), arguments.history)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
    print(result)


if __name__ == "__main__":
    main()
