import os.path
import re

from setuptools import find_packages, setup

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(
    os.path.join(this_directory, "ssrspeed/__init__.py"), mode="r", encoding="utf-8"
) as v:
    version = re.findall(r'__version__ = "(.*?)"', v.read())[0]

with open(os.path.join(this_directory, "README.md"), mode="r", encoding="utf-8") as f:
    long_description = f.read()

with open(
    os.path.join(this_directory, "requirements.txt"), mode="r", encoding="utf-8"
) as r:
    install_requires = [i.strip() for i in r]

setup(
    name="ssrspeed",
    version=version,
    keywords=["ssr", "speed", "test"],
    url="https://github.com/OreosLab/SSRSpeedN",
    license="GPL-3.0 License",
    description="A simple tool to test nodes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["ssrspeed", "ssrspeed.*"]),
    include_package_data=True,
    python_requires=">=3.8.0",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["ssrspeed = ssrspeed.__main__:main"]},
)
