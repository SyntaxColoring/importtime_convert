from __future__ import annotations

import dataclasses
import itertools
import re
import typing


def parse(
    # todo: Might want to take my own advice here and use a less restrictive
    # protocol instead of typing.TextIO. https://stackoverflow.com/questions/38569401
    input: typing.TextIO,
) -> list[Import]:
    lines = _parse_lines(input)
    nodes = _grow_tree(lines)
    return nodes


@dataclasses.dataclass
class Import:
    self_us: int
    cumulative_us: int
    package: str
    children: list[Import]


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
                    children=[node[1] for node in nodes_to_adopt],
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
