from __future__ import annotations

import dataclasses
import io
import typing

import pytest

from import_time_flame_graph._parse import Node, parse


def test_column_parsing() -> None:
    """Test basic extraction of values from columns."""
    input = """\
import time: self [us] | cumulative | imported package
import time:         1 |          2 | foo
import time:        33 |         44 | bar
import time:       555 |        666 | foo._bar.baz
"""
    result = parse(io.StringIO(input))
    assert result == [
        Node(self_us=1, cumulative_us=2, imported_package="foo", children=[]),
        Node(self_us=33, cumulative_us=44, imported_package="bar", children=[]),
        Node(
            self_us=555, cumulative_us=666, imported_package="foo._bar.baz", children=[]
        ),
    ]


def test_junk_filtering() -> None:
    """Test that junk interspersed with the `-X importtime` output is ignored."""
    input = """\
blah
import time: self [us] | cumulative | imported package
blah
import time:         1 |          2 | foo
blah
yak yak import time:        33 |         44 | bar
blah
import time:       555 |        666 | foo._bar.baz
blah
"""
    result = parse(io.StringIO(input))
    assert result == [
        Node(self_us=1, cumulative_us=2, imported_package="foo", children=[]),
        Node(self_us=33, cumulative_us=44, imported_package="bar", children=[]),
        Node(
            self_us=555, cumulative_us=666, imported_package="foo._bar.baz", children=[]
        ),
    ]


@pytest.mark.parametrize("include_trailing_newline", [True, False])
def test_trailing_newline(include_trailing_newline: bool) -> None:
    """Trailing newlines should be tolerated but not required."""
    input = """\
import time: self [us] | cumulative | imported package
import time:         1 |          2 | foo"""
    assert not input.endswith("\n")
    if include_trailing_newline:
        input += "\n"

    result = parse(io.StringIO(input))
    assert result == [
        Node(self_us=1, cumulative_us=2, imported_package="foo", children=[]),
    ]


def test_tree_structure() -> None:
    """Test that the tree structure is inferred correctly and order is preserved."""
    input = """\
import time: self [us] | cumulative | imported package
import time:         0 |          0 |     asyncio.base_subprocess
import time:         0 |          0 |     asyncio.selector_events
import time:         0 |          0 |   asyncio.unix_events
import time:         0 |          0 | asyncio
import time:         0 |          0 |       unittest.util
import time:         0 |          0 |     unittest.result
import time:         0 |          0 |       difflib
import time:         0 |          0 |     unittest.case
import time:         0 |          0 |   unittest
import time:         0 |          0 |       importlib._abc
import time:         0 |          0 |     importlib.util
import time:         0 |          0 |   pkgutil
import time:         0 |          0 | unittest.mock
"""
    result = parse(io.StringIO(input))
    simplified_result = _simplify_tree(result)

    expected_result: list[_SimplifiedNode] = [
        {
            "p": "asyncio",
            "c": [
                {
                    "p": "asyncio.unix_events",
                    "c": [
                        {"p": "asyncio.base_subprocess", "c": []},
                        {"p": "asyncio.selector_events", "c": []},
                    ],
                }
            ],
        },
        {
            "p": "unittest.mock",
            "c": [
                {
                    "p": "unittest",
                    "c": [
                        {
                            "p": "unittest.result",
                            "c": [{"p": "unittest.util", "c": []}],
                        },
                        {
                            "p": "unittest.case",
                            "c": [{"p": "difflib", "c": []}],
                        },
                    ],
                },
                {
                    "p": "pkgutil",
                    "c": [
                        {
                            "p": "importlib.util",
                            "c": [{"p": "importlib._abc", "c": []}],
                        }
                    ],
                },
            ],
        },
    ]

    assert simplified_result == expected_result


def _simplify_tree(tree: list[Node]) -> list[_SimplifiedNode]:
    """Convert a parsed tree into a dict structure, for more convenient comparison against literals."""

    def simplify_node(entries: list[tuple[str, typing.Any]]) -> _SimplifiedNode:
        original = dict(entries)
        simplified = {"p": original["imported_package"], "c": original["children"]}
        return simplified  # type: ignore

    return [dataclasses.asdict(node, dict_factory=simplify_node) for node in tree]


class _SimplifiedNode(typing.TypedDict):
    p: str
    """This node's package name."""
    c: list[_SimplifiedNode]
    """This node's children."""
