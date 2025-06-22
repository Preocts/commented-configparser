"""Custom ConfigParser class that preserves comments when writing loaded config out."""

from __future__ import annotations

import io
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

_COMMENT_PATTERN = re.compile(r"^\s*[#|;]\s*(.*)$")
_BLANK_LINE_PATTERN = re.compile(r"^\s*$")
_COMMENT_OPTION_PATTERN = re.compile(r"^(\s*)?__comment_\d+\s?[=|:]\s?(.*)$")
_KEY_PATTERN = re.compile(r"^(.+?)\s?[=|:].*$")
_SECTION_PATTERN = re.compile(r"^\s*\[(.+)\]\s*$")


class CommentedConfigParser(ConfigParser):
    """Custom ConfigParser that preserves comments when writing a loaded config out."""

    def read(
        self,
        filenames: StrOrBytesPath | Iterable[StrOrBytesPath],
        encoding: str | None = None,
    ) -> list[str]:
        # Re-implementing the parent method so that the handling of file
        # contents can be routed through .read_file(). Otherwise injecting
        # the comment translation is more difficult.
        if isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]

        # This only exists in 3.10+ and assists with unifying encoding.
        if hasattr(io, "text_encoding"):  # pragma: no cover
            encoding = io.text_encoding(encoding)

        read_ok = []
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self.read_file(fp)

            except OSError:
                continue

            if isinstance(filename, os.PathLike):
                filename = os.fspath(filename)
            read_ok.append(str(filename))

        return read_ok

    def read_file(self, f: Iterable[str], source: str | None = None) -> None:
        content = self._translate_comments([line for line in f])
        self.__is_reading = True
        super().read_file(content.splitlines(), source)
        self.__is_reading = False

    def optionxform(self, optionstr: str) -> str:
        if hasattr(self, "_CommentedConfigParser__is_reading") and self.__is_reading:
            return optionstr

        return super().optionxform(optionstr)

    def write(
        self,
        fp: SupportsWrite[str],
        space_around_delimiters: bool = True,
    ) -> None:
        capture_output = StringIO()
        super().write(capture_output, space_around_delimiters)
        rendered_output = self._restore_comments(capture_output.getvalue())

        fp.write(rendered_output)

    def _translate_comments(self, content: list[str]) -> str:
        """Translate comments to section options while storing header."""
        seen_section = False

        # To save the pain of mirroring ConfigParser's __init__ these two
        # attributes are created in the instance here, when needed.
        if not hasattr(self, "_CommentedConfigParser__header_block"):
            self.__header_block: list[str] = []

        if not hasattr(self, "_CommentedConfigParser__file_index"):
            self.__file_index = 0

        translated_lines = []
        for idx, line in enumerate(content):
            if _SECTION_PATTERN.match(line):
                seen_section = True

            if not seen_section:
                # Assume lines before a section are comments. If they are not
                # the parent class will raise the needed exceptions for an
                # invalid config format.
                self.__header_block.append(line)

            elif _COMMENT_PATTERN.match(line):
                # Translate the comment into an option for the section. These
                # are handled by the parent and retain order of insertion.
                line = f"__comment_{self.__file_index}{idx}={line.lstrip()}"

            elif _BLANK_LINE_PATTERN.match(line):
                # Blank lines cannot be stripped or the newline char will
                # be lost which causes issues downstream.
                line = f"__comment_{self.__file_index}{idx}={line}"

            elif _KEY_PATTERN.match(line) or _SECTION_PATTERN.match(line):
                # Strip the left whitespace from sections and keys. This will
                # leave only multiline values with leading whitespace preventing
                # the saved output from incorrectly indenting after a comment
                # when the loaded config contains indented sections.
                line = line.lstrip()

            translated_lines.append(line)

        # If additional configuration files are loaded, comments may end up sharing
        # idx values which will clobber previously loaded comments.
        self.__file_index += 1

        return "".join(translated_lines)

    def _restore_comments(self, content: str) -> str:
        """Restore comment options to comments."""
        # Apply the headers before parsing the config lines
        rendered = []
        if hasattr(self, "_CommentedConfigParser__header_block"):
            rendered += self.__header_block

        for line in content.splitlines():
            if not line:
                # Skip the provided empty lines and use our own instead
                continue

            comment_match = _COMMENT_OPTION_PATTERN.match(line)
            if comment_match:
                line = comment_match.group(2)

            rendered.append(line + "\n")

        return "".join(rendered)
