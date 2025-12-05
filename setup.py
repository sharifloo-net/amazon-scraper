from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="amazon-scraper",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A professional Amazon price tracker and monitoring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharifloo-net/amazon-scraper",
    packages=find_packages(exclude=["tests*"]),
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "amazon-scraper=scraper.cli:main",
        ],
    },
)