import typing

from ._parse import Import


def to_flamegraph_pl(nodes: list[Import]) -> str:
    def get_lines() -> typing.Iterator[str]:
        for path in _all_paths(nodes):
            weight = path[-1].self_us
            path_str = ";".join(node.package for node in path)
            yield f"{path_str} {weight}"

    return "\n".join(get_lines()) + "\n"


def _all_paths(nodes: typing.Iterable[Import]) -> typing.Iterable[list[Import]]:
    def _all_paths_internal(
        node: Import, prefix: list[Import]
    ) -> typing.Iterable[list[Import]]:
        this_prefix = prefix + [node]
        for child in node.children:
            yield from _all_paths_internal(child, this_prefix)
        yield this_prefix

    for node in nodes:
        yield from _all_paths_internal(node, prefix=[])
