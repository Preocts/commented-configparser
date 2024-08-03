"""Custom ConfigParser class that preserves comments when writing loaded config out."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from configparser import ConfigParser
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath
    from _typeshed import SupportsWrite

__all__ = ["CommentedConfigParser"]

COMMENT_PATTERN = re.compile(r"^\s*[#|;].+$")
COMMENT_OPTION_PATTERN = re.compile(r"^(\s*)?__comment_\d+[=|:](.*)$")
KEY_PATTERN = re.compile(r"^(.+?)[=|:].*$")
SECTION_PATTERN = re.compile(r"^\s*\[(.+)\]\s*$")


class CommentedConfigParser(ConfigParser):
    """Custom ConfigParser that preserves comments when writing a loaded config out."""

    def __init__(self) -> None:
        self._headers: list[str] = []
        super().__init__()

    def optionxform(self, optionstr: str) -> str:
        return optionstr

    def read(
        self,
        filenames: StrOrBytesPath | Iterable[StrOrBytesPath],
        encoding: str | None = None,
    ) -> list[str]:
        if isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]

        for filename in filenames:
            content = self._fileload(filename, encoding)
            self._translate_comments(content)

        return super().read(filenames, encoding)

    def read_file(self, f: Iterable[str], source: str | None = None) -> None:
        content = [line for line in f]
        self._translate_comments(content)

        return super().read_file(content, source)

    def write(
        self,
        fp: SupportsWrite[str],
        space_around_delimiters: bool = True,
    ) -> None:
        capture_output = StringIO()
        super().write(capture_output, space_around_delimiters)

        rendered_output = self._restore_comments(capture_output.getvalue())

        fp.write(rendered_output)

    def _fileload(
        self,
        filepath: StrOrBytesPath,
        encoding: str | None = None,
    ) -> str | None:
        """Load a file if it exists."""
        try:
            with open(filepath, encoding=encoding) as infile:
                return infile.read()
        except OSError:
            return None

    def _get_key(self, line: str) -> str:
        """
        Return the key of a line trimmed of leading/trailing whitespace.

        Respects both `=` and `:` delimiters, uses which happens first. If
        the line contains neither, the entire line is returned.
        """
        # Find which of the two assigment delimiters is used first
        matches = KEY_PATTERN.match(line)
        return matches.group(1).strip() if matches else line.strip()

    def _translate_comments(self, content: str | list[str] | None) -> str | None:
        """Translate comments to section options while storing header."""
        if content is None:
            return content

        # The header contains any comments that arrive before a section
        # is declared. These cannot be translated to options and must
        # be stored internally.
        header = []
        seen_section = False

        if isinstance(content, str):
            content_lines = content.split("\n") if content is not None else []
        else:
            content_lines = content

        translated_lines = []
        for idx, line in enumerate(content_lines):
            if SECTION_PATTERN.match(line):
                seen_section = True

            if not seen_section:
                # Assume lines before a section are comments. If they are not
                # the parent class will raise the needed exceptions for an
                # invalid config format.
                header.append(line)

            elif COMMENT_PATTERN.match(line):
                # Translate the comment into an option for the section. These
                # are handled by the parent and retain order of insertion.
                line = f"__comment_{idx}={line}"

            translated_lines.append(line)

        return "\n".join(translated_lines)

    def _restore_comments(self, content: str) -> str:
        """Restore comment options to comments."""
        # Apply the headers before parsing the config lines
        rendered = [] + self._headers

        for line in content.splitlines():
            comment_match = COMMENT_OPTION_PATTERN.match(line)
            if comment_match:
                line = comment_match.group(2)

            rendered.append(line)

        return "\n".join(rendered)
