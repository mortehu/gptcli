from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gptcli",
    version="0.1.0",
    author="Morten Hustveit",
    author_email="morten.hustveit@gmail.com",
    description="A command line program to interact with GPT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gptcli",
    packages=find_packages(),
    package_data={
        "gptcli": ["prompt_prefix.txt"],
    },
    python_requires=">=3.6",
    install_requires=[
    entry_points={
        "console_scripts": [
            "hey_gpt=gptcli.hey_gpt:main",
        ],
    },
)
