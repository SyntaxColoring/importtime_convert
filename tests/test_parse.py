from __future__ import annotations

import subprocess
import sys
import typing

import pytest

from importtime_convert import Import, parse


def test_column_parsing() -> None:
    """Test basic extraction of values from columns."""
    input = """\
import time: self [us] | cumulative | imported package
import time:         1 |          2 | foo
import time:        33 |         44 | bar
import time:       555 |        666 | foo._bar.baz
"""
    result = parse(input)
    assert result == [
        Import(self_us=1, cumulative_us=2, package="foo", subimports=[]),
        Import(self_us=33, cumulative_us=44, package="bar", subimports=[]),
        Import(self_us=555, cumulative_us=666, package="foo._bar.baz", subimports=[]),
    ]


def test_junk_filtering() -> None:
    """Test that junk interspersed with the `-X importtime` output is ignored.

    We expect to be able to ignore junk that occupies a full line, and junk that
    occupies the beginning of a line. The latter can happen if something does
    `print(sys.stderr, "blah", end=None)`.
    """
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
    result = parse(input)
    assert result == [
        Import(self_us=1, cumulative_us=2, package="foo", subimports=[]),
        Import(self_us=33, cumulative_us=44, package="bar", subimports=[]),
        Import(self_us=555, cumulative_us=666, package="foo._bar.baz", subimports=[]),
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

    result = parse(input)
    assert result == [
        Import(self_us=1, cumulative_us=2, package="foo", subimports=[]),
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
    result = parse(input)
    simplified_result = _simplify_tree(result)

    expected_result: list[_SimplifiedImport] = [
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


@pytest.mark.parametrize(
    "packages",
    [
        ["re"],
        ["asyncio"],
        ["unittest.mock"],
        ["importtime_convert"],
        ["re", "asyncio", "unittest.mock", "importtime_convert"],
    ],
)
def test_live(packages: list[str]) -> None:
    """Try parsing the actual `-X importtime` output of the current Python interpreter.

    The intent here is to catch if the `-X importtime` output format changes in
    some future Python version.
    """
    raw_output = _do_x_importtime(packages)
    raw_output_lines = raw_output.splitlines()

    # We expect the first line to be a header:
    header_line = raw_output_lines[0]
    assert "import time" in header_line
    assert "self" in header_line
    assert "cumulative" in header_line
    assert "imported package" in header_line

    # Extract the "imported package" part of each row, including indentation, e.g.
    # foo
    #   bar
    # baz
    raw_output_package_column = [line.split("|")[-1] for line in raw_output_lines[1:]]

    def depth_first_packages_and_levels(
        imports: list[Import], root_level: int = 0
    ) -> typing.Iterator[tuple[str, int]]:
        for import_ in imports:
            yield from depth_first_packages_and_levels(
                import_.subimports, root_level + 1
            )
            yield import_.package, root_level

    # From the result of our parsing, reconstruct what the original "imported package"
    # column ought to have looked like, including indentation. It should match exactly.
    parsed = parse(raw_output)
    parsed_packages_and_levels = depth_first_packages_and_levels(parsed)
    reconstructed_package_column = [
        " " * (level * 2 + 1) + package
        for (package, level) in parsed_packages_and_levels
    ]

    assert reconstructed_package_column == raw_output_package_column


def _do_x_importtime(packages: list[str]) -> str:
    python_command = ";".join(f"import {package}" for package in packages)
    assert sys.executable
    cli_command = [sys.executable, "-X", "importtime", "-c", python_command]
    output = subprocess.run(
        cli_command,
        capture_output=True,
        check=True,
    )
    return output.stderr.decode("ascii")


def _simplify_tree(tree: list[Import]) -> list[_SimplifiedImport]:
    """Pare down the nested dict structure for more convenient comparison against literals."""

    def _simplify_import(import_: Import) -> _SimplifiedImport:
        return _SimplifiedImport(
            p=import_.package,
            c=[_simplify_import(child) for child in import_.subimports],
        )

    return [_simplify_import(import_) for import_ in tree]


class _SimplifiedImport(typing.TypedDict):
    p: str
    """This node's package name."""
    c: list[_SimplifiedImport]
    """This node's children."""
