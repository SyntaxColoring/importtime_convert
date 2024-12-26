import argparse
import json
import sys
import textwrap
import typing

from . import __version__
from ._output_formats import to_flamegraph_pl, to_json_serializable
from ._parse import Import, parse


def _cli_main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m importtime_convert",  # Python >=3.14 could do this automatically.
        description=textwrap.dedent(
            """\
            Convert the output of `python -X importtime ...` to other formats.

            This tool always expects the `-X importtime` data to be provided on stdin, and always sends the converted output to stdout.

            stdin is allowed to contain stuff other than `-X importtime` data, like stray log messages. It will be filtered out and ignored.
            """
        ),
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,  # Preserve line breaks.
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "--output-format",
        "-o",
        choices=["flamegraph.pl", "json"],
        required=True,
        help=textwrap.dedent(
            """\
            Select the output format."

            flamegraph.pl: For flame graph generation tools. The format is defined by Brendan Gregg's flamegraph.pl script, but other flame graph tools accept it, too.

            json: A simple JSON format specific to this tool.
            """
        ),
    )

    args = parser.parse_args()
    output_format: typing.Literal["flamegraph.pl", "json"] = args.output_format

    imports = parse(sys.stdin)

    if output_format == "flamegraph.pl":
        sys.stdout.write(to_flamegraph_pl(imports))
    elif output_format == "json":
        _write_json_str(imports, sys.stdout)
    else:
        typing.assert_never(output_format)


def _write_json_str(imports: list[Import], dest: typing.TextIO) -> None:
    json.dump(to_json_serializable(imports), dest, indent=2)
    dest.write("\n")


if __name__ == "__main__":
    _cli_main()
