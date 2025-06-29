from setuptools import setup

setup(
    name="pydns",
    version="0.1.1",
    packages=["pydns"],
    install_requires=[],
    entry_points={
        "console_scripts": ["pydns = pydns.cli:parse_args"]
    },
)
