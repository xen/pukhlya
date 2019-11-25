import os
import re
import pathlib
from typing import List

from setuptools import find_packages, setup

REGEXP = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
PARENT = pathlib.Path(__file__).parent


def read_version():
    init_py = PARENT / "pukhlya" / "__init__.py"

    with init_py.open() as f:
        for line in f:
            match = REGEXP.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = f"Cannot find version in ${init_py}"
            raise RuntimeError(msg)


def read_requirements(path: str) -> List[str]:
    file_path = PARENT / path
    with open(file_path) as f:
        return f.read().split("\n")


setup(
    name="pukhlya",
    version=read_version(),
    description="Pukhlya is AIOHTTP simple and ready-to-go admin for SQLAlchemy models",
    platforms=["POSIX"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    zip_safe=False,
)
