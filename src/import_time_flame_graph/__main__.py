from __future__ import annotations

import sys

from ._output_format import to_gregg
from ._parse import parse


def _cli_main() -> int:
    nodes = parse(sys.stdin)
    sys.stdout.write(to_gregg(nodes))
    return 0


if __name__ == "__main__":
    sys.exit(_cli_main())
