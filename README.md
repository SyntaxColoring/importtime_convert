## Overview

This is a CLI tool and small library to parse the output of [`python -X importtime ...`](https://docs.python.org/3/using/cmdline.html#cmdoption-X) and convert it to other formats. Use it to help visualize and understand your Python import times—for example, by generating [flame graphs](https://www.brendangregg.com/flamegraphs.html).

## Installation

With `pip`:

```
pip install importtime_convert
importtime-convert --help
```

Or with [`pipx`](https://pipx.pypa.io/):

```
pipx run importtime-convert --help
```

## Usage as a CLI tool

The CLI tool is spelled `importtime-convert` or `python -m importtime_convert`. Give it the raw `python -X importtime ...` data on stdin, and it will output the converted result on stdout.

Here's a typical usage example, with Bash redirection syntax:

```bash
# Python outputs its raw importtime data to stderr. Save it to raw_importtime.txt.
python -X importtime -c 'import module_to_test' 2> raw_importtime.txt

# Convert it to "flamegraph.pl" format, and save that to converted_importtime.txt.
importtime-convert --output-format flamegraph.pl <raw_importtime.txt >converted_importtime.txt
```

Or, all in one step:

```bash
python -X importtime -c 'import module_to_test' \
    2>&1 >/dev/null \
    | importtime-convert --output-format flamegraph.pl \
    > converted_importtime.txt
```

See the [available output formats](#available-output-formats) below and `importtime-convert --help` for full details.

## Usage as a library

The following are available from `import importtime_convert`:

### `parse(input: typing.TextIO | str) -> list[Import]`

`parse()` takes the raw `-X importtime` data, as a string or as a file-like object. It returns the parsed import structure as a list of **top-level** imports. The list is in the order that the interpreter traversed them.

### `Import`

An `Import` is a dataclass with the following keys:

* `package: str`: The full package path of this import, e.g. `"foo.bar"`.
* `cumulative_us: int`: The time, in microseconds, that the interpreter spent on this module, including any subimports.
* `self_us: int`: The time, in microseconds, that the interpreter spent on this module, *not* including any subimports.
* `subimports: list[Import]`: This module's subimports. The list is in the order that the interpreter traversed them.

### Output conversion functions

* `to_flamegraph_pl(imports: list[Import]) -> str`
* `to_json_serializable(imports: list[Import]) -> list[dict[str, Any]]`

See the [available output formats](#available-output-formats) below for details.

## Available output formats

* **`--output-format flamegraph.pl` (CLI) / `to_flamegraph_pl()` (API)**

  For [flame graph](https://www.brendangregg.com/flamegraphs.html) generation tools.

  The format is defined by [Brendan Gregg's flamegraph.pl script](https://github.com/brendangregg/FlameGraph), but other flame graph tools accept it, too. (For example, https://www.speedscope.app/ and https://flamegraph.com/.)

* **`--output-format json` (CLI) / `to_json_serializable()` (API)**

  A simple JSON format specific to this tool. Looks like this:

  ```json
  [
    {
      "package": "foo",
      "self_us": 200,
      "cumulative_us": 300,
      "subimports": [
        {
          "package": "bar",
          "self_us": 100,
          "cumulative_us": 100,
          "subimports": []
        }
      ]
    },
    {
      "package": "baz.baz",
      "self_us": 100,
      "cumulative_us": 100,
      "subimports": []
    }
  ]
  ```

  See [the API docs above](#Import) for the meanings of the fields.

Feature requests and pull requests are welcome for additional output formats.

## Related work and alternatives

* https://github.com/asottile/importtime-waterfall
* https://github.com/dominikwalk/importtime-output-wrapper
* https://github.com/kmichel/python-importtime-graph
* https://github.com/nschloe/tuna
