# Basic setup

1. Ensure you've installed at least one of the versions of Python that's supported by this project.
2. [Install Nox](https://nox.thea.codes/).

Then:

* Run `nox` to run the full suite of typechecks, tests, etc. It should autodetect your installed Python versions. If you have a lot of Python versions installed, this can take a while; you can limit it to just one version with `nox --python <version>`.
* To run a specific task (what `nox` calls a "session"), run `nox -s <session name>`. See `nox --list` for all available session names.
* Run `nox -s make_dev_venv` to create a virtual environment at `.venv/` that has this project and its dev dependencies installed. Point your editor to it so it can follow imports and give you autocomplete.

# Release checklist

1. Make sure the release notes are updated.
2. Bump the version numbers in `__init__.py` and `pyproject.toml`.
3. Make sure CI passes on GitHub.
4. Tag the release: `git tag --annotate -m "Release v1.2.3." v1.2.3 && git push origin v1.2.3`
5. Run the deployment workflow on GitHub. It will build the project, then wait for publish approval, then publish to PyPI.
6. Manually test the PyPI release with `pip install` in a throwaway venv.
