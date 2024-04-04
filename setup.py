"""Handle module packaging."""

import re
import subprocess
import textwrap

from setuptools import setup

RE_VERSION = re.compile(r"(\d+\.\d+\.\d+)")


def _get_release_version() -> str:
    """Get git release tag version."""
    version_match = RE_VERSION.search(
        subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .strip()
    )
    version = version_match[0] if version_match else "0.0.0"
    print("Release version: ", version)
    return version


def _write_version(version: str) -> None:
    """Write version to version.py."""
    with open("src/hassapi/version.py", "w") as file:
        file.write(
            textwrap.dedent(
                f'''
                """Host package version, generated on build."""
                __version__ = "{version}"
                '''
            ).lstrip()
        )


version = _get_release_version()
_write_version(version)
setup(version=version)