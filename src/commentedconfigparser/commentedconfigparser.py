"""
Custom ConfigParser class that preserves comments when writing a loaded config out.

"""
from __future__ import annotations

import re
from pathlib import Path

COMMENT = re.compile(r"\s*[#|;]")


class CommentConfig:
    """Custom ConfigParser that preserves comments when writing a loaded config out."""

    def __init__(self, filepath: str | None = None) -> None:
        """Load file if provided."""
        self._comment_map: dict[str, list[str]] = {}

        if filepath:
            self.load(filepath)

    def load(self, filepath: str) -> None:
        """
        Load a file. Will replace any previously loaded file.

        Args:
            filepath: path to target file, will raise if missing.
        """
        content = Path(filepath).read_text()

        for content_line in content.split("\n"):
            self._is_comment(content_line)

    def _is_comment(self, line: str) -> bool:
        """True if the line is a valid ini comment."""
        return bool(COMMENT.search(line))
