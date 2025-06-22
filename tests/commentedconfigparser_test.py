from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from commentedconfigparser import commentedconfigparser
from commentedconfigparser.commentedconfigparser import CommentedConfigParser


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
        ("#", True),
        ("#\t", True),
    ),
)
def test_comment_pattern(line: str, expected: bool) -> None:
    result = commentedconfigparser._COMMENT_PATTERN.match(line)

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
    result = commentedconfigparser._SECTION_PATTERN.match(line)

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
        ("\tkey with spaces=value", "\tkey with spaces"),
        ("\tkey: value with = in it", "\tkey"),  # both delimiters
        ("\tkey=val:ues", "\tkey"),  # both delimiter equal spacing
    ),
)
def test_key_pattern(line: str, expected: str) -> None:

    match = commentedconfigparser._KEY_PATTERN.match(line)

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

    match = commentedconfigparser._COMMENT_OPTION_PATTERN.match(line)

    assert match
    assert match.group(2) == expected


def test_regression_read_loads_normally_list() -> None:
    cc = CommentedConfigParser()

    read = cc.read(["tests/regression_original_input.ini", "notfoundatall.ini"])

    assert len(read) == 1


def test_regression_read_loads_normally_single_file() -> None:
    cc = CommentedConfigParser()

    read = cc.read("tests/regression_original_input.ini")

    assert len(read) == 1


def test_regression_read_file_normally() -> None:
    cc = CommentedConfigParser()

    with open("tests/regression_original_input.ini") as file:
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


def test_write_with_no_comments() -> None:
    cc = CommentedConfigParser()
    expected = "[TEST]\ntest=pass\n"
    cc.read_dict({"TEST": {"test": "pass"}})
    mock_file = StringIO()

    cc.write(mock_file, space_around_delimiters=False)

    assert mock_file.getvalue() == expected


@pytest.mark.parametrize(
    ("ini_in", "ini_expected"),
    (
        (["empty_comments_input.ini"], "empty_comments_expected.ini"),
        (["header_input.ini"], "header_expected.ini"),
        (["pydocs_input.ini"], "pydocs_expected.ini"),
        (["regression_original_input.ini"], "regression_original_expected.ini"),
        (["multi02_input.ini", "multi01_input.ini"], "multi_expected.ini"),
    ),
)
def test_reading_and_writing_config_files(
    ini_in: list[str],
    ini_expected: str,
    tmp_path: Path,
) -> None:
    tmp_file = tmp_path / "test_reading_and_writing.ini"
    expected = (Path("tests") / ini_expected).read_text(encoding="utf-8")
    config = CommentedConfigParser()
    config.read([Path("tests") / file for file in ini_in])

    with open(tmp_file, "w", encoding="utf-8") as outfile:
        config.write(outfile)

    with open(tmp_file, encoding="utf-8") as infile:
        contents = infile.read()

    assert contents == expected


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


def test_regression_keys_are_treated_as_case_insensitive() -> None:
    configdict = {"default": {"FoO": "BAR"}}
    config = CommentedConfigParser()
    config.read_dict(configdict)

    assert config.get("default", "Foo") == "BAR"
