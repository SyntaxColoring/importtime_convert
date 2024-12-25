"""Parse the output of `python -X importtime` and convert it to other formats."""

# Re-exports:
from ._output_format import to_flamegraph_pl as to_flamegraph_pl
from ._parse import Import as Import
from ._parse import parse as parse

__version__ = "0"
