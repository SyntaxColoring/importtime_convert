# Basic setup

[Install Nox](https://nox.thea.codes/).

Then:

* Run `nox` to run the full suite of typechecks, tests, etc.
* To run a specific thing, run `nox -s <session name>`. See `nox --list` for all available session names.
* Run `nox -s make_dev_venv` to create a virtual environment at `.venv/` that has this project and its dev dependencies installed. Point your editor to it so it can follow imports and give you autocomplete.
