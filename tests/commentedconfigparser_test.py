from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from commentedconfigparser import commentedconfigparser
from commentedconfigparser.commentedconfigparser import CommentedConfigParser

CONFIG_W_COMMENTS = "tests/withcomments.ini"


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("# This is a comment", True),
        ("; This is a comment", True),
        ("  \t; This is a comment", True),
        ("  \t# This is a comment", True),
        ("This is a comment", False),
        ("  \tThis is a comment", False),
        ("", False),
        ("  \t", False),
    ),
)
def test_comment_pattern(line: str, expected: bool) -> None:
    result = commentedconfigparser.COMMENT_PATTERN.match(line)

    assert bool(result) is expected


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("\t[SECTION]", True),
        ("\t[SECTION", False),
        ("    [SECTION]", True),
        ("SECTION]", False),
        ("# [SECTION]", False),
        ("", False),
    ),
)
def test_section_pattern(line: str, expected: bool) -> None:
    result = commentedconfigparser.SECTION_PATTERN.match(line)

    assert bool(result) is expected


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("key = value", "key"),
        ("key=value", "key"),
        ("key=:value", "key"),
        ("key:=value", "key"),
        ("key : value", "key"),
        ("key:value", "key"),
        ("\tkey with spaces=value", "key with spaces"),
        ("\tkey: value with = in it", "key"),  # both delimiters
        ("\tkey=val:ues", "key"),  # both delimiter equal spacing
        ("\t[SECTION name]", "[SECTION name]"),
        ("", ""),
    ),
)
def test_key_pattern(line: str, expected: str) -> None:

    match = commentedconfigparser.KEY_PATTERN.match(line)

    assert match
    assert match.group(1) == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("__comment_123 = # Some comment", "# Some comment"),
        ("__comment_1 = \t\t# Some comment", "\t\t# Some comment"),
        ("__comment_123 =", ""),
    ),
)
def test_comment_option_pattern(line: str, expected: str) -> None:

    match = commentedconfigparser.COMMENT_OPTION_PATTERN.match(line)

    assert match
    assert match.group(2) == expected


def test_regression_read_loads_normally_list() -> None:
    cc = CommentedConfigParser()

    read = cc.read([CONFIG_W_COMMENTS, "notfoundatall.ini"])

    assert len(read) == 1


def test_regression_read_loads_normally_single_file() -> None:
    cc = CommentedConfigParser()

    read = cc.read(CONFIG_W_COMMENTS)

    assert len(read) == 1


def test_regression_read_file_normally() -> None:
    cc = CommentedConfigParser()

    with open(CONFIG_W_COMMENTS) as file:
        cc.read_file(file)

    assert cc.get("NEW SECTION", "closing") == "0"


def test_regression_read_string_loads_normally() -> None:
    cc = CommentedConfigParser()

    cc.read_string("[TEST]\ntest=pass")

    assert cc.get("TEST", "test") == "pass"


def test_regression_read_dict_loads_normally() -> None:
    cc = CommentedConfigParser()

    cc.read_dict({"TEST": {"test": "pass"}})

    assert cc.get("TEST", "test") == "pass"


def test_regression_write_normally() -> None:
    cc = CommentedConfigParser()
    expected = "[TEST]\ntest=pass\n"
    cc.read_string(expected)
    mock_file = StringIO()

    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == expected


def test_fileload() -> None:
    cc = CommentedConfigParser()

    result = cc._fileload("tests/withcomments.ini")

    assert result
    assert "[NEW SECTION]" in result


def test_fileload_silently_fails() -> None:
    cc = CommentedConfigParser()

    result = cc._fileload("tests/notherefile.ini")

    assert result is None


def test_write_with_no_comments() -> None:
    cc = CommentedConfigParser()
    expected = "[TEST]\ntest=pass\n\n"
    cc.read_dict({"TEST": {"test": "pass"}})
    mock_file = StringIO()

    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == expected


def test_issue_46_duplicating_sections(tmp_path: Path) -> None:
    # https://github.com/Preocts/commented-configparser/issues/46
    tmp_file = tmp_path / "issue46_test_file.ini"
    starting_config = "[example]\nfoo = 0\n"
    expected = "[example]\nfoo = 9\n"
    tmp_file.write_text(starting_config, "utf-8")
    cc = CommentedConfigParser()
    cc.read(tmp_file)

    # v1 bug which duplicated sections when explicily writing the config back
    # to file in a loop which was using .set(...)
    for idx in range(10):
        cc.set("example", "foo", str(idx))
        with open(tmp_file, "w", encoding="utf-8") as outfile:
            cc.write(outfile)

    assert tmp_file.read_text("utf-8") == expected
