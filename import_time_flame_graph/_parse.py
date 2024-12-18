from __future__ import annotations

import itertools
import re
import sys
import typing


def parse(
    # todo: Might want to take my own advice here and use a less restrictive
    # protocol instead of typing.TextIO. https://stackoverflow.com/questions/38569401
    input: typing.TextIO
) -> list[Node]:
    lines = itertools.islice(
        input,
        1,  # Skip the header line.
        None,
    )

    # Filter out junk that didn't come from `-X importtime`, e.g. random stderr messages.
    # This also filters out blank lines.
    lines = (line for line in lines if line.startswith("import time:"))

    lines = (_parse_line(line) for line in lines)

    lines = _group_indents(list(lines))

    nodes = _grow_tree(lines)

    return nodes


class Node(typing.NamedTuple):
    self_us: int
    cumulative_us: int
    imported_package: str
    children: list[Node]


class InputFormatError(ValueError):
    def __init__(self, bad_line: str) -> None:
        self.bad_line = bad_line


class _ParsedLine(typing.NamedTuple):
    self_us: int
    cumulative_us: int
    raw_indentation_length: int
    imported_package: str


def _group_indents(
    lines: list[_ParsedLine],
) -> typing.Iterable[_ParsedLine | typing.Literal["begin_group", "end_group"]]:
    # TODO: This reversal is for easier implementation of this
    # function (it's easier to keep track of things if we can
    # guarantee that we only increase by one level of indentation at a time)
    # but it does reverse the
    reversed_lines = reversed(lines)
    indentation_stack: list[int] = []
    for line in reversed_lines:
        if not indentation_stack:
            yield "begin_group"
            indentation_stack.append(line.raw_indentation_length)

        previous_indentation_level = indentation_stack[-1]
        indentation_change = line.raw_indentation_length - previous_indentation_level

        if indentation_change > 0:  # Indentation got deeper.
            yield "begin_group"
            indentation_stack.append(line.raw_indentation_length)
        else:
            while line.raw_indentation_length < indentation_stack[-1]:
                yield "end_group"
                indentation_stack.pop()
        yield line


def _grow_tree(parsed_lines: typing.Iterable[_ParsedLine | typing.Literal["begin_group", "end_group"]]) -> list[Node]:
    result: list[Node] = []

    for line in parsed_lines:
        if line == "begin_group":
            children = _grow_tree(parsed_lines)
            if result:
                parent = result[-1]
                parent.children[:] = children
            else:
                result.extend(children)
        elif line == "end_group":
            return result
        else:
            result.append(
                Node(
                    self_us=line.self_us,
                    cumulative_us=line.cumulative_us,
                    imported_package=line.imported_package,
                    children=[]
                )
            )

    return result

# Example:
# import time:   12 |        345 |     foo._bar.baz
_pattern = re.compile(
    r"import time:"
    r"\s*"
    r"(?P<self_us>[0-9]+)"
    r"\s*\|\s*"
    r"(?P<cumulative_us>[0-9]+)"
    r"\s\|"
    r"(?P<indentation> *)(?P<package>.*)"
    r"\n?"
)


def _parse_line(line: str) -> _ParsedLine:
    match = re.fullmatch(_pattern, line)
    if match is None:
        raise InputFormatError(bad_line=line)
    return _ParsedLine(
        self_us=int(match["self_us"]),
        cumulative_us=int(match["cumulative_us"]),
        raw_indentation_length=len(match["indentation"]),
        imported_package=match["package"],
    )
