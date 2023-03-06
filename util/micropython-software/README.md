# MicroPython Tests

## Building

locally:

`docker build -t micropython .`

### Downloading the image remotely

The ECS gitlab container registry is not publicly available, so you need to create an SSH tunnel to log in and download the image.

In a different terminal, create an SSH session with ports 4567 forwarded to the gitlab server:

```shell
ssh -L 4567:gitlab.ecs.vuw.ac.nz:4567 username@greta-pt.ecs.vuw.ac.nz
```

In your main terminal, log in:

```shell
docker login localhost:4567
```

(enter your ecs credentials)

Download the image:

```shell
docker pull localhost:4567/course-work/engr301/2023/group<n>/data-recorder/micropython
```

## Running tests

The GitLab CI script is currently set to run "hello world".

Once the software tests have been written, modify `.gitlab-ci.yml` to point to the path for the test script.

## Running MicroPython locally

`docker run -it micropython` (the `micropython` image would likely be different if pulled from the ECS server rather than built locally)

---
