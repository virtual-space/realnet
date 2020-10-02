import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="realnet",
    version="0.0.11",
    description="Realnet command line interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/virtual-space/realnet",
    author="Marko Laban",
    author_email="marko.laban@l33tsystems.com",
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["pynecone==0.0.61",
                      "realnet-core==0.0.13",
                      "python-jsonstore==1.2.0",
                      "bleak",
                      "pybluez",
                      "tabulate"],
    entry_points={
        "console_scripts": [
            "realnet=realnet.__main__:main",
        ]
    },
)
