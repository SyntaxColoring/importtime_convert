import textwrap

from importtime_convert import Import, to_flamegraph_pl
from importtime_convert._output_formats import to_json_serializable


def test_to_flamegraph_pl() -> None:
    input = [
        Import(
            package="a",
            self_us=100,
            cumulative_us=999,
            subimports=[
                Import(
                    package="b",
                    self_us=200,
                    cumulative_us=999,
                    subimports=[
                        Import(
                            package="c",
                            self_us=300,
                            cumulative_us=999,
                            subimports=[],
                        )
                    ],
                ),
                Import(package="d", self_us=400, cumulative_us=999, subimports=[]),
            ],
        ),
        Import(package="e", self_us=500, cumulative_us=999, subimports=[]),
    ]
    output = to_flamegraph_pl(input)
    expected_output = textwrap.dedent(
        """\
        a;b;c 300
        a;b 200
        a;d 400
        a 100
        e 500
        """
    )
    assert output == expected_output


def test_to_json() -> None:
    input = [
        Import(
            package="a",
            self_us=101,
            cumulative_us=102,
            subimports=[
                Import(package="b", self_us=201, cumulative_us=202, subimports=[])
            ],
        ),
        Import(package="c", self_us=301, cumulative_us=302, subimports=[]),
    ]
    output = to_json_serializable(input)
    expected_output = [
        {
            "package": "a",
            "self_us": 101,
            "cumulative_us": 102,
            "subimports": [
                {"package": "b", "self_us": 201, "cumulative_us": 202, "subimports": []}
            ],
        },
        {"package": "c", "self_us": 301, "cumulative_us": 302, "subimports": []},
    ]
    assert output == expected_output
