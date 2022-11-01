from __future__ import annotations

import pytest
from commentedconfigparser.commentedconfigparser import CommentConfig


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
    cc = CommentConfig()

    result = cc._is_comment(line)

    assert result is expected
