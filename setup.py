from pathlib import Path
import io
import os
import sys
import re
from shutil import rmtree
from typing import List

from setuptools import find_packages, setup, Command

REGEXP = re.compile(r'^__version__\W*=\W*"([\d.abrc]+)"')
DESCRIPTION = "Pukhlya is AIOHTTP simple and ready-to-go admin for SQLAlchemy models"

here = Path(__file__).parent


def read_requirements(path: str) -> List[str]:
    file_path = here / path
    with open(file_path) as f:
        return f.read().split("\n")


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(Path.absolute(here / "README.md"), encoding="utf-8") as f:
        LONG_DESCR = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCR = DESCRIPTION


def read_version():
    init_py = here / "pukhlya" / "__init__.py"

    with init_py.open() as f:
        for line in f:
            match = REGEXP.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = f"Cannot find version in {init_py}"
            raise RuntimeError(msg)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(Path.absolute(here / "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(read_version()))
        os.system("git push --tags")

        sys.exit()


setup(
    name="pukhlya",
    version=read_version(),
    description="Pukhlya is AIOHTTP simple and ready-to-go admin for SQLAlchemy models",
    long_description=LONG_DESCR,
    long_description_content_type="text/markdown",
    author="Mikhail Kashkin",
    author_email="m@xen.ru",
    platforms=["POSIX"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    zip_safe=False,
    keywords=["admin", "aiohttp", "sqlalchemy", "wtforms"],
    classifiers=[
        "Framework :: AsyncIO",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Session",
    ],
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
