# Util Directory

Contents of this directory:

- `micropython-software` - micropython tests ran under docker. High level business logic code - nothing hardware specific.
- `micropython-hitl` - hardware-in-the-loop tests. In CI, ran by a custom runner that has a devkit attached.
  - `pyboard.py` standalone micropython tool. [Documentation](https://docs.micropython.org/en/latest/reference/pyboard.py.html). Used to run code on the devices
- `scripts`:
  - `commit-lint.sh` - commit message linter (deprecated - using gitlint)

## CI/CD (DevOps) Overview

A big part of DevOps is Continuous Integration and Continuous Delivery, collectively sometimes referred to as CI/CD.

Continuous Integration (CI) is the practice of automating the integration of code changes through compilation, static analysis and testing.
Meanwhile, Continuous Delivery (CD) is a development approach that prioritises short software release cycles, in an effort to build and release software at a greater speed and accuracy while also reducing cost, time and risks.

We make use of DevOps practices such as CI/CD to reinforce the Agile software development methodology employed in the project, and to ensure consistently high quality software was being written.
In particular, Hardware-in-the-loop testing was built to run automated code tests on real world hardware.
Linting tools are used to enforce a standard code-writing style, and CD pipelines allow automated typesetting and delivery of updated academic reports.
This section briefly discusses the rationale, design and implementation of these techniques.

## Docker-Based Testing

A _Dockerfile_ was built to install the Micropython Unix port into a Docker Image.
This image was uploaded to the ECS GitLab.
_GitLab CI/CD_ has the ability to use Docker images as the basis for running automated pipelines.
When a new CI job is created from a git push or branch merge, it creates a container from the uploaded Micropython image, setting the entrypoint of the container to run the test suite from the device code.

The benefits of this approach is that the high level logic of the embedded software could be evaluated and tested quickly.
With no resource constraints (in comparison to the devices), the scripts could run quickly and hence feed back timely information to the developers.

However, the speed benefits come at a cost of flexibility.
The Unix port implements a subset of the Micropython standard library, so some functions, especially hardware-specific or low-level, do not work.
Furthermore, resource constraints (such as low available RAM, clock speed) do not exist, so it is hard to get a realistic estimate of how the code would perform on the embedded device.
As a result, the docker-based tests are useful for testing high level code and algorithms.

## Hardware-In-The-Loop (HITL) testing

HITL tests were designed to address the limitations of docker-based software tests mentioned above.
HITL uses a custom GitLab Runner on a Raspberry Pi connected to an ESP32 dev-kit over USB.
A script was written that compiles and uploads the latest code to the dev-kit, runs the HITL tests included in the compiled code, and returns an exit code based on the results.
See [HITL Readme](micropython-hitl/README.md) for a technical overview of how HITL tests run.

The benefits of this approach is that code runs _directly on the hardware we are using in the project_.
If a test fails here, it is extremely likely to fail in the field.
HITL tests enable a high sense of confidence in writing high quality low-level code.
This is especially important for hardware drivers, discussed in the Hardware Report.

The downsides of HITL testing is speed - it takes longer to run the HITL tests than it does on docker, so the number of HITL based tests should be minimised, instead focussing on useful, hardware-centric tests.
Testing software components, especially high-level code, should remain in the docker test suite.
Another downside of HITL testing is that jobs can't be run in parallel - while not a problem right now, in the future jobs could get queued up, slowing down the CI pipelines as the ESP32 can only run one test at a time.
We could get around this if we bought multiple ESP32s to plug into the gitlab runner machine, although this could get complicated and unreliable trying to manage lots of serial devices.

Unfortunately, the serial connection to the ESP32 was fairly unstable and due to time constraints, HITL tests were temporarily disabled.
We plan on re-enabling the HITL tests later in the year - probably around iteration 2, when we will focus on building the first prototype device.

## Linting and Static Analysis

Static Analysis is a method of inspecting code without running the program.
In our project, we use Black for linting code, and a custom bash script for linting Git commit messages.

Black, the uncompromising code formatter' forces developers to cede control over the formatting of python code.
It's deterministic and strict linting rules are enforced through Gitlab CI, preventing poor style from being committed to the master code branch.
Code is formatted as it is written using pre-commit hooks.

Black was compared against other formatting tools, such as Flake8 and Pylint.
While all do a good job of linting code against the standard PEP8, Black enforces the code style extremely strictly, and its auto-formatting tools allows us to focus on writing code, rather than manually fixing the errors.

Git commit messages are checked by [gitlint](https://jorisroovers.com/gitlint/) which enforces a modified Angular Commit style.
The benefit of this is that it is easy to see at a glance the scope, type and changes of a commit.
As a result, reviews, debugging and auditing code changes are more accessible and faster to perform.

## CD: LaTeX Report Typesetting

Gitlab CI automatically typesets the academic LaTeX reports, and stores the output as a build artifact from the Job.
It does this using a custom Docker image that works similarly to the Docker tests described above.
The image contains all the necessary scripts and style files required to build the reports.
The primary benefit of CI-based typesetting is that the client, project supervisor and team members can always read the latest compiled version of a report for review.
This comes at a small performance decrease - the LaTeX files are always built, regardless of the commit type - but they only take a matter of seconds to build, so are considered acceptable.
