# Development Environment Setup

Table of Contents:

- [Development Environment Setup](#development-environment-setup)
  - [Overview](#overview)
    - [Dependencies](#dependencies)
    - [Preferred IDE - Visual Studio Code](#preferred-ide---visual-studio-code)
  - [Setup Instructions](#setup-instructions)

These instructions are intended to help get a development environment set up.

We have successfully developed this project on Ubuntu 20.04, MacOS 1.15, and on Windows 10 through WSL (Ubuntu 20.04).

The embedded software is written in Python 3, and the Webapp code is written in Javascript.

## Overview

### Dependencies

The following dependencies are **required**:

- **git**
- **python 3.9** or greater
- **nodeJS v14.21.3** or greater (with **npm v8.6.0** or greater)
 - **It would be ideal to use the latest nodeJS version** (following are confirmed to be working):
    - Node.js 20.2.0
    - Node.js 19.9.0
    - Node.js 18.16.0
    - Node.js 17.9.1
    - Node.js 16.20.0
    - Node.js 15.14.0
    - Node.js 14.21.3

The following dependencies are **preferred**:

- **pyenv** for managing python versions. There's an automated installer [here](https://github.com/pyenv/pyenv-installer).
- **virtualenv** for managing virtual environments. If using `pyenv`, use [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) too.

### Preferred IDE - Visual Studio Code

Any code editor that supports python and javascript is sufficient for this project - be aware that micropython has some libraries pre-baked that aren't availble in Pypi (such as `machine`), so linting plugins will fail to resolve their imports.

If using Windows, install the [Remote WSL extension](https://code.visualstudio.com/docs/remote/wsl-tutorial).

## Setup Instructions

Firstly, ensure the dependencies above are installed. The following resources are useful:

- **macOS**: Install `pyenv` with homebrew - `brew install pyenv`
- Install node with [Node Version Manager](https://github.com/nvm-sh/nvm).
- install virtualenv locally with `pip3 install --user virtualenv`

Clone the repository locally with git:

```bash
git clone git@gitlab.ecs.vuw.ac.nz:course-work/engr301/2023/group<n>/data-recorder.git
```

If using `virtualenv`, activate the virtual environment:

```bash
virtualenv venv --python=python3.9
source venv/bin/activate
```

A virtual environment is a tool to create isolated python environments, so that the libraries we install for the project won't affect the python installation on your OS.
Note that we've standardized on using the name `venv` as the local folder containing the virtual environment.

Install the python dependencies:

```bash
pip install -r requirements.txt
```

We use [pre-commit](https://pre-commit.com/) to automatically run python linting, git commit message linting, and other checks. It is enforced by CI. Install the hooks with:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

From [a note](https://jorisroovers.com/gitlint/#using-gitlint-through-pre-commit) specifying why the second line is important:

> It's important that you run `pre-commit install --hook-type commit-msg`, even if you've already used `pre-commit install` before. `pre-commit install` does **not** install commit-msg hooks by default!

Next, set up the Webapp development environment by following the instructions [here](/software/device/webapp/README.md).
