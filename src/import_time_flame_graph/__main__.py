from __future__ import annotations

import sys

from ._parse import parse, InputFormatError
from ._output_format import to_gregg


def _cli_main() -> int:
    try:
        nodes = parse(sys.stdin)
    except InputFormatError as e:
        print(sys.stderr, "Error parsing line:")
        print(sys.stderr, e.bad_line)
        return 1
    else:
        sys.stdout.write(to_gregg(nodes))
        return 0


if __name__ == "__main__":
    sys.exit(_cli_main())
