"""Setup script to install mensautils as a package"""

from setuptools import find_namespace_packages, setup

REQUIREMENTS = open("requirements.txt").read().splitlines()

setup(
    name="mensautils",
    packages=find_namespace_packages(),
    install_requires=REQUIREMENTS,
)
