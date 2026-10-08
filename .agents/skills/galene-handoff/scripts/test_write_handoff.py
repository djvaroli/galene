"""Exercise record storage in temporary Git fixtures, never a live handoff."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from write_handoff import write_handoff


class HandoffWriterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="galene-handoff-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def test_replacement_preserves_previous_brief(self):
        previous = "Unfinished review: 保持\n".encode()
        self.assertEqual(write_handoff(self.root, previous), self.root / ".HANDOFF")
        write_handoff(self.root, b"Next increment\n")
        self.assertEqual((self.root / ".HANDOFF").read_bytes(), b"Next increment\n")
        history = list((self.root / ".handoff").glob("*.md"))
        self.assertEqual([record.read_bytes() for record in history], [previous])
        self.assertFalse(list((self.root / ".handoff").glob("*.tmp")))

    def test_history_note_keeps_current_brief(self):
        write_handoff(self.root, b"Current state\n")
        note = write_handoff(self.root, b"Investigation result\n", history_only=True)
        self.assertEqual(note.parent, self.root / ".handoff")
        self.assertEqual(note.read_bytes(), b"Investigation result\n")
        self.assertEqual((self.root / ".HANDOFF").read_bytes(), b"Current state\n")

    def test_tracked_destinations_are_preserved(self):
        for name in (".HANDOFF", ".handoff/previous.md"):
            with self.subTest(name=name):
                destination = self.root / name
                destination.parent.mkdir(exist_ok=True)
                destination.write_bytes(b"Tracked record\n")
                subprocess.run(["git", "-C", str(self.root), "add", "--", name], check=True)
                with self.assertRaisesRegex(ValueError, "records are tracked"):
                    write_handoff(self.root, b"Must not replace\n")
                self.assertEqual(destination.read_bytes(), b"Tracked record\n")
                subprocess.run(
                    ["git", "-C", str(self.root), "rm", "--cached", "-q", "--", name],
                    check=True,
                )
                destination.unlink()

    def test_symlink_destinations_are_rejected(self):
        for name in (".HANDOFF", ".handoff"):
            for history_only in (False, True):
                with self.subTest(name=name, history_only=history_only):
                    target = self.root / "outside-record"
                    link = self.root / name
                    link.symlink_to(target)
                    with self.assertRaisesRegex(ValueError, "Unsafe record destination"):
                        write_handoff(self.root, b"Must not write\n", history_only)
                    self.assertTrue(link.is_symlink())
                    self.assertFalse(target.exists())
                    link.unlink()

    def test_wrong_destination_types_are_preserved(self):
        brief = self.root / ".HANDOFF"
        brief.mkdir()
        with self.assertRaisesRegex(ValueError, "Expected an ordinary file"):
            write_handoff(self.root, b"Must not write\n")
        self.assertTrue(brief.is_dir())
        brief.rmdir()
        history = self.root / ".handoff"
        history.write_bytes(b"Keep this file\n")
        with self.assertRaisesRegex(ValueError, "Expected an ordinary directory"):
            write_handoff(self.root, b"Must not write\n")
        self.assertEqual(history.read_bytes(), b"Keep this file\n")

    def test_failed_publication_preserves_brief_and_history(self):
        write_handoff(self.root, b"Current state\n")
        prior = write_handoff(self.root, b"Prior findings\n", history_only=True)
        with patch.object(Path, "replace", side_effect=OSError("Publication failed")):
            with self.assertRaisesRegex(OSError, "Publication failed"):
                write_handoff(self.root, b"Replacement\n")
        self.assertEqual((self.root / ".HANDOFF").read_bytes(), b"Current state\n")
        self.assertEqual(prior.read_bytes(), b"Prior findings\n")
        self.assertEqual(list((self.root / ".handoff").iterdir()), [prior])


if __name__ == "__main__":
    unittest.main()
