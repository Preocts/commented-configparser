from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from commentedconfigparser.commentedconfigparser import CommentedConfigParser

CONFIG_W_COMMENTS = "tests/withcomments.ini"
CONFIG_W_COMMENTS_STR = Path("tests/withcomments.ini").read_text()
EXPECTED_MAP = {
    "@@header": ["# Welcome to our config"],
    "[DEFAULT]": [
        "# This value has some meaning to someone",
    ],
    "foo": [
        "# Make sure to add this when you need it",
    ],
    "logging": [
        "; This is a comment as well",
        "",
        "# so we need to track all of them",
        "",
        "    ; and many could be between things",
    ],
    "[NEW SECTION]": [
        "# Another comment",
    ],
    "closing": [""],
}


def test_assert_class_var_is_always_empty() -> None:
    assert CommentedConfigParser._comment_map is None


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("# This is a comment", True),
        ("; This is a comment", True),
        ("  \t; This is a comment", True),
        ("  \t# This is a comment", True),
        ("This is a comment", False),
        ("  \tThis is a comment", False),
        ("", True),
        ("  \t", True),
    ),
)
def test_is_comment_or_empty(line: str, expected: bool) -> None:
    cc = CommentedConfigParser()

    result = cc._is_comment_or_empty(line)

    assert result is expected


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
def test_get_line_key(line: str, expected: str) -> None:
    cc = CommentedConfigParser()

    result = cc._get_key(line)

    assert result == expected


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
    expected = "[TEST]\ntest=pass\n\n"
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


def test_map_comments() -> None:
    cc = CommentedConfigParser()
    expected = json.dumps(EXPECTED_MAP)

    cc._map_comments(CONFIG_W_COMMENTS_STR)
    assert cc._comment_map
    result = json.dumps(cc._comment_map)

    assert result == expected


def test_read_file_captures_comments() -> None:
    cc = CommentedConfigParser()
    expected = json.dumps(EXPECTED_MAP)

    with open(CONFIG_W_COMMENTS) as file:
        cc.read_file(file)
    result = json.dumps(cc._comment_map)

    assert result == expected


def test_read_captures_comments_single_file() -> None:
    cc = CommentedConfigParser()
    expected = json.dumps(EXPECTED_MAP)

    cc.read(CONFIG_W_COMMENTS)
    result = json.dumps(cc._comment_map)

    assert result == expected


def test_read_string_captures_comments() -> None:
    cc = CommentedConfigParser()
    expected = json.dumps(EXPECTED_MAP)

    cc.read_string(CONFIG_W_COMMENTS_STR)
    result = json.dumps(cc._comment_map)

    assert result == expected
