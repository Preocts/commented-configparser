from __future__ import annotations

import pytest
from commentedconfigparser.commentedconfigparser import CommentedConfigParser


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        ("# This is a comment", True),
        ("; This is a comment", True),
        ("  ; This is a comment", True),
        ("  # This is a comment", True),
        ("This is a comment", False),
        ("  This is a comment", False),
        ("", False),
    ),
)
def test_is_comment(line: str, expected: bool) -> None:
    cc = CommentedConfigParser()

    result = cc._is_comment(line)

    assert result is expected


def test_regression_read_reads() -> None:
    cc = CommentedConfigParser()

    read = cc.read(["tests/withcomments.ini", "notfoundatall.ini"])

    assert len(read) == 1


def test_regression_read_string_loads_normally() -> None:
    cc = CommentedConfigParser()

    cc.read_string("[TEST]\ntest=pass")

    assert cc.get("TEST", "test") == "pass"


def test_regression_read_dict_loads_normally() -> None:
    cc = CommentedConfigParser()

    cc.read_dict({"TEST": {"test": "pass"}})

    assert cc.get("TEST", "test") == "pass"
