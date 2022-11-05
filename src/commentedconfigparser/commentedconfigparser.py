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

COMMENT_PTN = re.compile(r"^\s*[#|;]")
KEY_PTN = re.compile("^(.+?)[=|:]")
SECTION_PTN = re.compile(r"^\s*\[(.+)\]\s*$")


class CommentedConfigParser(ConfigParser):
    """Custom ConfigParser that preserves comments when writing a loaded config out."""

    _comment_map: dict[str, dict[str, list[str]]] | None = None

    def read(
        self,
        filenames: StrOrBytesPath | Iterable[StrOrBytesPath],
        encoding: str | None = None,
    ) -> list[str]:

        if isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]

        for filename in filenames:
            content = self._fileload(filename, encoding)
            self._map_comments(content)

        return super().read(filenames, encoding)

    def read_file(self, f: Iterable[str], source: str | None = None) -> None:

        content = [line for line in f]
        self._map_comments("".join(content))

        return super().read_file(content, source)

    def write(
        self, fp: SupportsWrite[str], space_around_delimiters: bool = True
    ) -> None:
        # Early exit if the config was never loaded with comments (from_dict/run-time)
        if self._comment_map is None:
            return super().write(fp, space_around_delimiters)

        capture_output = StringIO()
        super().write(capture_output, space_around_delimiters)

        self._merge_deleted_keys()

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

    def _is_comment(self, line: str) -> bool:
        """True if the line is a valid ini comment."""
        return bool(COMMENT_PTN.search(line))

    def _is_empty(self, line: str) -> bool:
        """True if line is just whitesspace."""
        return not bool(re.sub(r"\s*", "", line))

    def _is_section(self, line: str) -> bool:
        """True if line is a section."""
        return bool(SECTION_PTN.search(line))

    def _get_key(self, line: str) -> str:
        """
        Return the key of a line trimmed of leading/trailing whitespace.

        Respects both `=` and `:` delimiters, uses which happens first. If
        the line contains neither, the entire line is returned.
        """
        # Find which of the two assigment delimiters is used first
        matches = KEY_PTN.match(line)
        return matches.group(1).strip() if matches else line.strip()

    def _map_comments(self, content: str | None) -> None:
        """Map comments of config internally for restoration on write."""
        # The map holds comments that happen under the given key
        # @@header is an arbatrary section and key assigned to
        # capture the top of a file or section.
        section = "@@header"
        key = "@@header"

        content_lines = content.split("\n") if content is not None else []
        comment_lines: list[str] = []
        comment_map = self._comment_map if self._comment_map else {}

        for line in content_lines:
            # Define the section or use existing
            comment_map[section] = comment_map.get(section, {})

            if self._is_comment(line):
                comment_lines.append(line)

            # We allow empty lines to be ignored giving the library
            # control over general line spacing format.
            elif not self._is_empty(line):
                # Update the current section, clear, and start again
                comment_map[section][key] = comment_lines.copy()
                comment_lines.clear()

                # Figure out if we have a key or a new section
                if self._is_section(line):
                    # TODO: Probably should rename this method. _get_token() ?
                    section = self._get_key(line)
                    key = "@@header"
                else:
                    key = self._get_key(line)

        # Capture all trailing lines in comment_lines on exit of loop
        comment_map[section][key] = comment_lines.copy()

        self._comment_map = comment_map

    def _restore_comments(self, content: str) -> str:
        """Restore comments from internal map."""
        if self._comment_map is None:
            # This should never be needed
            return content

        section = "@@header"
        key = "@@header"
        # Apply the headers before parsing the config lines
        rendered: list[str] = self._comment_map[section].get(key, [])

        for line in content.splitlines():
            # Order of reconstruction is config-line then any comments
            rendered.append(line)

            if self._is_section(line):
                section = self._get_key(line)
                key = "@@header"
            else:
                key = self._get_key(line)

            rendered.extend(self._comment_map.get(section, {}).get(key, []))

        return "\n".join(rendered)

    def _merge_deleted_keys(self) -> None:
        """Find and merges comments of deleted keys up the comment_map tree."""
        if self._comment_map is None:
            return

        orphaned_comments: list[str] = []
        # Walk the sections and keys backward so we merge 'up'.
        for section in list(self._comment_map.keys())[::-1]:
            section_mch = SECTION_PTN.match(section)
            if section_mch is None:
                # Strange that we have a section value that isn't a valid section
                continue

            for key in list(self._comment_map[section])[::-1]:

                # Key no longer exists, gather comments and loop upward
                if key != "@@header" and not self.has_option(section_mch.group(1), key):

                    # Comments need to be stored in reverse order to avoid
                    # needing to insert into front of list
                    orphaned_comments.extend(self._comment_map[section].pop(key)[::-1])

                elif section_mch.group(1) in self.keys():
                    # Drop everything in the next key that exists
                    # If the section is gone carry all comments up to bottom of next
                    # Reverve the order as they were added in reverse
                    self._comment_map[section][key].extend(orphaned_comments[::-1])
                    orphaned_comments.clear()

            # Remove sections that should now be empty
            if not section_mch.group(1) in self.keys():
                self._comment_map.pop(section)

        # All remaining orphans moved to the top of the file
        self._comment_map["@@header"]["@@header"].extend(orphaned_comments[::-1])
