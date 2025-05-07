"""Parse the output of `python -X importtime` and convert it to other formats."""

# Re-exports:
from ._output_formats import to_flamegraph_pl as to_flamegraph_pl
from ._output_formats import to_json_serializable as to_json_serializable
from ._parse import Import as Import
from ._parse import parse as parse

__version__ = "1.1.0"
