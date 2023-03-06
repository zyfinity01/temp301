# HITL Testing

## Resources

- [good introduction to using rshell](https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-iii-building-a-micropython-application)

## Process

HITL (Hardware in the loop testing) is a method of testing that integrates real hardware in the test process.
The `hitl-tests.sh` script first uploads the latest code to the device using `rshell`, then uses `pyboard.py` to copy the device test suite into ram and then run it.
The script greps the test output for "FAIL" and returns an error code if failures were found.

## Runner Setup

The HITL runner is currently on a raspbery pi model 3 B+ with a fresh install of Rasbian Buster.

Setup instructions:

Connect the HITL device via USB. Install apt package `picocom` and test serial communication works with `pycocom /dev/ttyUSB0`

Install gitlab-runner

```shell
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install -y gitlab-runner
```

Register the runner

```shell
sudo gitlab-runner register
```

Add gitlab-runner user to dialout and tty groups

```shell
sudo usermod -aG dialout gitlab-runner
sudo usermod -aG tty gitlab-runner
```

Manually install packages onto the runner

```shell
sudo pip3 install pyboard rshell
```

---
