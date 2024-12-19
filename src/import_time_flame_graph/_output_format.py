import typing

from ._parse import Node


def to_gregg(nodes: list[Node]) -> str:
    def get_lines() -> typing.Iterator[str]:
        for path in _all_paths(nodes):
            weight = path[-1].self_us
            path_str = ";".join(node.imported_package for node in path)
            yield f"{path_str} {weight}"

    return "\n".join(get_lines()) + "\n"


def _all_paths(nodes: typing.Iterable[Node]) -> typing.Iterable[list[Node]]:
    def _all_paths_internal(
        node: Node, prefix: list[Node]
    ) -> typing.Iterable[list[Node]]:
        this_prefix = prefix + [node]
        for child in node.children:
            yield from _all_paths_internal(child, this_prefix)
        yield this_prefix

    for node in nodes:
        yield from _all_paths_internal(node, prefix=[])
