"""
Custom ConfigParser class that preserves comments when writing a loaded config out.

"""
from __future__ import annotations

import re
from collections.abc import Iterable
from configparser import ConfigParser
from os import PathLike
from pathlib import Path
from typing import Union

StrOrBytesPath = Union[str, bytes, "PathLike[str]", "PathLike[bytes]"]
COMMENT_PTN = re.compile(r"\s*[#|;]")
KEY_PTN = re.compile("(.+?)[=|:]")


class CommentedConfigParser(ConfigParser):
    """Custom ConfigParser that preserves comments when writing a loaded config out."""

    _comment_map: dict[str, list[str]] | None = None

    def read(
        self,
        filenames: StrOrBytesPath | Iterable[StrOrBytesPath],
        encoding: str | None = None,
    ) -> list[str]:
        return super().read(filenames, encoding)

    def read_file(self, f: Iterable[str], source: str | None = None) -> None:
        return super().read_file(f, source)

    def read_string(self, string: str, source: str = "<string>") -> None:
        return super().read_string(string, source)

    def _fileload(self, filepath: str) -> str | None:
        """Load a file if it exists."""
        # TODO: This will need to handle StrOrBytesPath and file-likes
        path = Path(filepath)
        return path.read_text() if path.exists() else None

    def _is_comment_or_empty(self, line: str) -> bool:
        """True if the line is a valid ini comment."""
        return bool(COMMENT_PTN.search(line)) or not bool(re.sub(r"\s*", "", line))

    def _get_key(self, line: str) -> str:
        """
        Return the key of a line trimmed of leading/trailing whitespace.

        Respects both `=` and `:` delimiters, uses which happens first. If
        the line contains neither, the entire line is returned.
        """
        # Find which of the two assigment delimiters is used first
        matches = KEY_PTN.match(line)
        return matches.group(1).strip() if matches else line.strip()

    def _map_comments(self, config_name: str, content: str) -> None:
        """Map comments of config internally for restoration on write."""
        # The map holds comments that happen under the given key
        # @@header is an arbatrary keys assigned to capture the
        # top of the file.
        section = "@@header"
        comment_lines: list[str] = []
        comment_map = self._comment_map if self._comment_map else {}

        for line in content.split("\n"):
            if self._is_comment_or_empty(line):
                comment_lines.append(line)

            else:
                # Update the current section, clear, and start again
                comment_map[section] = comment_lines.copy()
                comment_lines.clear()
                section = self._get_key(line)

        # Capture all trailing lines in comment_lines on exit of loop
        comment_map[section] = comment_lines.copy()

        # Dischard any keys that have an empty value
        comment_map = {key: value for key, value in comment_map.items() if value}

        self._comment_map = comment_map
