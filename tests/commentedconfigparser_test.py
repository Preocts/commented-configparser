from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from commentedconfigparser.commentedconfigparser import CommentedConfigParser

CONFIG_W_COMMENTS = "tests/withcomments.ini"
CONFIG_W_COMMENTS_STR = Path("tests/withcomments.ini").read_text()
EXPECTED_MAP = {
    "@@header": {
        "@@header": [
            "# Welcome to our config",
        ],
    },
    "[DEFAULT]": {
        "@@header": [
            "# This value has some meaning to someone",
        ],
        "foo": [
            "# Make sure to add this when you need it",
        ],
        "trace": [],
        "logging": [
            "; This is a comment as well",
            "    # so we need to track all of them",
            "\t; and many could be between things",
        ],
    },
    "[NEW SECTION]": {
        "@@header": [],
        "foo": [
            "# Unique foo",
        ],
        "multi-line": [],
        "value01": [],
        "value02": [],
        "value03": [],
        "closing": [
            "# Trailing comment",
        ],
    },
}

# This is how we expect the withcomments.ini to re-render
# Use \t to render tabs. Will *not* match input file
EXPECTED_STR = Path("tests/expected.ini").read_text()


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
        ("", False),
        ("  \t", False),
    ),
)
def test_is_comment(line: str, expected: bool) -> None:
    cc = CommentedConfigParser()

    result = cc._is_comment(line)

    assert result is expected


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("  \tThis is a comment", False),
        ("", True),
        ("  \t", True),
        ("  ", True),
    ),
)
def test_is_empty(line: str, expected: bool) -> None:
    cc = CommentedConfigParser()

    result = cc._is_empty(line)

    assert result is expected


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("\t[SECTION]", True),
        ("\t[SECTION", False),
        ("    [SECTION]", True),
        ("SECTION]", False),
        ("", False),
    ),
)
def test_is_section(line: str, expected: bool) -> None:
    cc = CommentedConfigParser()

    result = cc._is_section(line)

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


def test_write_with_comments_single_file() -> None:
    cc = CommentedConfigParser()
    cc.read_string(CONFIG_W_COMMENTS_STR)
    mock_file = StringIO()

    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == EXPECTED_STR


def test_write_with_no_comments() -> None:
    cc = CommentedConfigParser()
    expected = "[TEST]\ntest=pass\n\n"
    cc.read_dict({"TEST": {"test": "pass"}})
    mock_file = StringIO()

    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == expected


def test_merge_deleted_keys() -> None:
    cc = CommentedConfigParser()
    cc.read_dict({"TEST": {}})
    cc._comment_map = {"[TEST]": {"@@header": [], "test": ["# Test comment"]}}

    cc._merge_deleted_keys("[TEST]")

    assert cc._comment_map == {"[TEST]": {"@@header": ["# Test comment"]}}


def test_write_with_comments_single_file_remove_key() -> None:
    cc = CommentedConfigParser()
    mod_expected = EXPECTED_STR.replace("foo=bar\n", "", 1)
    cc.read_string(CONFIG_W_COMMENTS_STR)
    mock_file = StringIO()

    cc.remove_option("DEFAULT", "foo")
    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == mod_expected
