from __future__ import annotations

import dataclasses
import io
import itertools
import re
import typing


def parse(
    # todo: Might want to take my own advice here and use a less restrictive
    # protocol instead of typing.TextIO. https://stackoverflow.com/questions/38569401
    input: str | typing.TextIO,
) -> list[Import]:
    """Parse raw data from `-X importtime` into an import tree.

    Returns the list of top-level imports, in the order that the interpreter
    traversed them.
    """
    if isinstance(input, str):
        input = io.StringIO(input)
    lines = _parse_lines(input)
    nodes = _grow_tree(lines)
    return nodes


@dataclasses.dataclass
class Import:
    package: str
    """The full package path of this import, e.g. `"foo.bar"`."""

    self_us: int
    """The time, in microseconds, that the interpreter spent on this module, including any subimports."""

    cumulative_us: int
    """The time, in microseconds, that the interpreter spent on this module, *not* including any subimports."""

    subimports: list[Import]
    """This module's subimports. The list is in the order that the interpreter traversed them."""


@dataclasses.dataclass
class _ParsedLine:
    self_us: int
    cumulative_us: int
    raw_indentation_length: int
    imported_package: str


def _grow_tree(parsed_lines: typing.Iterable[_ParsedLine]) -> list[Import]:
    # List of (indentation_level, node) tuples.
    nodes_without_parent: list[tuple[int, Import]] = []

    for line in parsed_lines:
        nodes_to_adopt = list(
            itertools.takewhile(
                lambda n: n[0] > line.raw_indentation_length,
                reversed(nodes_without_parent),
            )
        )
        nodes_to_adopt.reverse()
        del nodes_without_parent[len(nodes_without_parent) - len(nodes_to_adopt) :]
        nodes_without_parent.append(
            (
                line.raw_indentation_length,
                Import(
                    self_us=line.self_us,
                    cumulative_us=line.cumulative_us,
                    package=line.imported_package,
                    subimports=[node[1] for node in nodes_to_adopt],
                ),
            )
        )

    return [node[1] for node in nodes_without_parent]


# import time:   12 |        345 |     foo._bar.baz
_pattern = re.compile(
    r".*"
    r"import time:"
    r"\s*"
    r"(?P<self_us>[0-9]+)"
    r"\s*\|\s*"
    r"(?P<cumulative_us>[0-9]+)"
    r"\s\|"
    r"(?P<indentation> *)(?P<package>.*)"
    r"\n?"
)


def _parse_lines(raw_lines: typing.Iterable[str]) -> typing.Iterator[_ParsedLine]:
    for raw_line in raw_lines:
        match = re.fullmatch(_pattern, raw_line)
        if match is not None:
            yield _ParsedLine(
                self_us=int(match["self_us"]),
                cumulative_us=int(match["cumulative_us"]),
                raw_indentation_length=len(match["indentation"]),
                imported_package=match["package"],
            )
