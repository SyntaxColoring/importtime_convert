# type: ignore
# nox is typically installed globally

import nox

SUPPORTED_PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(default=False)
def make_dev_venv(session):
    """Create a virtual environment for development.

    Point your editor to this so you get type hints for pytest and such.
    """
    session.run("python", "-m", "venv", ".venv")
    session.run(".venv/bin/pip", "install", "-r", "requirements-dev.txt", external=True)


@nox.session
def typecheck(session):
    """Do typechecking."""
    session.install("-r", "requirements-dev.txt")
    session.run("mypy", ".")


@nox.session(default=False)
def format(session):
    """Automatically fix formatting."""
    session.install("-r", "requirements-dev.txt")
    session.run("black", ".")
    session.run("isort", ".")


@nox.session
def format_check(session):
    """Check formatting."""
    session.install("-r", "requirements-dev.txt")
    session.run("black", "--check", ".")
    session.run("isort", "--check", ".")


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def test(session):
    """Run the package tests."""
    session.install("-r", "requirements-dev.txt")
    args = session.posargs or ["tests"]
    session.run("pytest", *args)


@nox.session(default=False)
def build(session):
    """Build the package distribution."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "-m", "build")
