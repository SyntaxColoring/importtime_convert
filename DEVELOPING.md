# Basic setup

1. Ensure you've installed at least one of the versions of Python that's supported by this project.
2. [Install Nox](https://nox.thea.codes/).

Then:

* Run `nox` to run the full suite of typechecks, tests, etc. It should autodetect your installed Python versions.
* To run a specific thing, run `nox -s <session name>`. See `nox --list` for all available session names.
* Run `nox -s make_dev_venv` to create a virtual environment at `.venv/` that has this project and its dev dependencies installed. Point your editor to it so it can follow imports and give you autocomplete.

# Release checklist

1. Make sure the release notes are updated.
2. Bump all version numbers.
3. Make sure CI passes on GitHub.
4. Run the deployment workflow on GitHub. It will build the project and publish it to PyPI.
5. Manually test the PyPI release with `pip install` in a throwaway venv.
