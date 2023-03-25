from pathlib import Path

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

current_directory = Path(__file__).parent.resolve()
long_description = (current_directory / "README.md").read_text(encoding="utf-8")


setup(
    name="arraydb",
    version="0.1.0",
    license="MIT",
    description="Database using array. With an basic ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Md Shahriyar Alam",
    author_email="contact@shahriyar.dev",
    keywords=["arraydb", "database"],
    url="https://github.com/shahriyardx/arraydb",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Database",
        "Operating System :: OS Independent",
    ],
)
