import textwrap

from importtime_convert import Import, to_flamegraph_pl


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
