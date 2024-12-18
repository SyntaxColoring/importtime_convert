# Overview

This is a script to convert the output of `python -X importtime` to a format suitable for generating a [flame graph](https://www.brendangregg.com/flamegraphs.html).

It is not very good yet.

# Usage

```bash
python -X importtime -c 'import module_to_test' 2> import_profile
python -m import_time_flame_graph <import_profile >import_profile_flamegraph
```

Then feed the output `import_profile_flamegraph` file to a flame graph viewer of your choice, such as:

* https://www.speedscope.app (my favorite)
* https://github.com/brendangregg/FlameGraph (the original)
