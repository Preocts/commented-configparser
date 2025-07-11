from __future__ import annotations

import os
import pathlib
import shutil
import sys
from functools import partial

import nox

# Control factors for finding pieces of the module
MODULE_NAME = "commentedconfigparser"
TESTS_PATH = "tests"
COVERAGE_FAIL_UNDER = 100
VENV_PATH = "./.venv"
LINT_PATH = "./src"
REQUIREMENTS_PATH = "./requirements"

LINTING_COMMANDS = (
    (
        "isort",
        "--verbose",
        "--force-single-line-imports",
        "--profile",
        "black",
        "--add-import",
        "from __future__ import annotations",
        LINT_PATH,
        TESTS_PATH,
    ),
    ("black", "--verbose", LINT_PATH, TESTS_PATH),
    ("flake8", "--show-source", "--verbose", LINT_PATH, TESTS_PATH),
    ("mypy", "--no-incremental", "--package", MODULE_NAME),
    ("mypy", "--no-incremental", TESTS_PATH),
)

# What we allowed to clean (delete)
CLEANABLE_TARGETS = [
    "./dist",
    "./build",
    "./.nox",
    "./.coverage",
    "./.coverage.*",
    "./coverage.json",
    "./**/.mypy_cache",
    "./**/.pytest_cache",
    "./**/__pycache__",
    "./**/*.pyc",
    "./**/*.pyo",
]

# Define the default sessions run when `nox` is called on the CLI
nox.options.default_venv_backend = "virtualenv"
nox.options.sessions = ["lint", "test"]


@nox.session()
def dev(session: nox.Session) -> None:
    """Setup a development environment by creating the venv and installs dependencies."""
    # Use the active environement if it exists, otherwise create a new one
    venv_path = os.environ.get("VIRTUAL_ENV", VENV_PATH)

    if sys.platform == "win32":
        venv_path = f"{venv_path}/Scripts"
        activate_command = f"{venv_path}/activate"
    else:
        venv_path = f"{venv_path}/bin"
        activate_command = f"source {venv_path}/activate"

    if not os.path.exists(VENV_PATH):
        session.run("python", "-m", "venv", VENV_PATH, "--upgrade-deps")

    python = partial(session.run, f"{venv_path}/python", "-m")
    contraint = ("--constraint", f"{REQUIREMENTS_PATH}/constraints.txt")

    python("pip", "install", "--editable", ".[dev,test]", *contraint, external=True)

    if not os.environ.get("VIRTUAL_ENV"):
        session.log(f"\n\nRun '{activate_command}' to enter the virtual environment.\n")


@nox.session(name="test")
def run_tests_with_coverage(session: nox.Session) -> None:
    """Run pytest with coverage, outputs console report and json."""
    print_standard_logs(session)

    contraint = ("--constraint", f"{REQUIREMENTS_PATH}/constraints.txt")

    session.install(".[test]", *contraint)

    coverage = partial(session.run, "python", "-m", "coverage")

    coverage("erase")

    if "partial-coverage" in session.posargs:
        coverage("run", "--parallel-mode", "--module", "pytest", TESTS_PATH)
    else:
        coverage("run", "--module", "pytest", TESTS_PATH)
        coverage("report", "--show-missing", f"--fail-under={COVERAGE_FAIL_UNDER}")
        coverage("json")


@nox.session()
def coverage_combine(session: nox.Session) -> None:
    """CI: Combine parallel-mode coverage files and produce reports."""
    print_standard_logs(session)

    contraint = ("--constraint", f"{REQUIREMENTS_PATH}/constraints.txt")

    session.install("-r", f"{REQUIREMENTS_PATH}/requirements-test.txt", *contraint)

    coverage = partial(session.run, "python", "-m", "coverage")
    coverage("combine")
    coverage("report", "--show-missing", f"--fail-under={COVERAGE_FAIL_UNDER}")
    coverage("json")


@nox.session(name="lint")
def run_linters_and_formatters(session: nox.Session) -> None:
    """Run code formatters, linters, and type checking against all files."""
    print_standard_logs(session)

    contraint = ("--constraint", f"{REQUIREMENTS_PATH}/constraints.txt")
    session.install(".[dev,test]", *contraint)

    python = partial(session.run, "python", "-m")

    for linter_command in LINTING_COMMANDS:
        python(*linter_command)


@nox.session()
def build(session: nox.Session) -> None:
    """Build distribution files."""
    print_standard_logs(session)

    session.install("build")
    session.run("python", "-m", "build")


@nox.session(name="update-deps")
def update_deps(session: nox.Session) -> None:
    """Process requirement*.txt files, updating only additions/removals."""
    print_standard_logs(session)

    session.install("pip-tools")
    session.run(
        "pip-compile",
        "--strip-extras",
        "--no-annotate",
        "--no-emit-index-url",
        "--output-file",
        f"{REQUIREMENTS_PATH}/constraints.txt",
        *get_requirement_files(),
    )


@nox.session(name="upgrade-deps")
def upgrade_deps(session: nox.Session) -> None:
    """Process requirement*.txt files and upgrade all libraries as possible."""
    print_standard_logs(session)

    session.install("pip-tools")
    session.run(
        "pip-compile",
        "--strip-extras",
        "--no-annotate",
        "--no-emit-index-url",
        "--upgrade",
        "--output-file",
        f"{REQUIREMENTS_PATH}/constraints.txt",
        *get_requirement_files(),
    )


@nox.session(python=False)
def clean(_: nox.Session) -> None:
    """Clean cache, .pyc, .pyo, and test/build artifact files from project."""
    count = 0
    for searchpath in CLEANABLE_TARGETS:
        for filepath in pathlib.Path(".").glob(searchpath):
            if filepath.is_dir():
                shutil.rmtree(filepath)
            else:
                filepath.unlink()
            count += 1

    print(f"{count} files cleaned.")


def print_standard_logs(session: nox.Session) -> None:
    """Reusable output for monitoring environment factors."""
    version = session.run("python", "--version", silent=True)
    session.log(f"Running from: {session.bin}")
    session.log(f"Running with: {version}")


def get_requirement_files() -> list[pathlib.Path]:
    """Get a list of requirement files matching "requirements*.txt"."""
    glob = pathlib.Path(REQUIREMENTS_PATH).glob("requirements*.txt")
    return [path for path in glob]
