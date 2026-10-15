"""Helper-AI: Autonomous PC Control & Internet Agent setup configuration."""
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

def parse_requirements(filename: str):
    reqs = []
    req_file = this_directory / filename
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    reqs.append(line)
    return reqs

setup(
    name="helper-ai",
    version="1.2.0",
    description="Autonomous PC Control & Internet Agent with Multi-Provider LLM Intelligence and Full Desktop Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rajkot Podman / Helper-AI Team",
    url="https://github.com/rajkotpodman/helper-AI",
    packages=find_packages(exclude=["tests*", "scratch*", "logs*", "browser_data*"]),
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.png", "*.svg", "*.ico", "*.json", "*.md"],
        "web": ["templates/*", "static/**/*"],
        "static": ["**/*"],
    },
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "helper-ai=app:run_server",
            "helper-ai-cli=helper:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.10",
)
