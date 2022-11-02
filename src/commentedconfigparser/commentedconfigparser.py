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
COMMENT = re.compile(r"\s*[#|;]")


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
        path = Path(filepath)
        return path.read_text() if path.exists() else None

    def _is_comment_or_empty(self, line: str) -> bool:
        """True if the line is a valid ini comment."""
        return bool(COMMENT.search(line)) or not bool(re.sub(r"\s*", "", line))
