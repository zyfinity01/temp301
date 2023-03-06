# HTLPi Build & Test Server

The configuration is specified as an Ansible playbook.

The current device name is `HTL` which was specified manually by `raspi-config`. Should find a way to do this via a command.

## Files

The files in this directory are the files which would have to be created/copied when a fresh version of the build & test server is provisioned.

### WiFi Configuration

The `wpa_supplicant.conf` file specifies the connection to the `WellingtonUniversityGuest` WiFi access point. The current Raspberry Pi 3B+ hardware was whitelisted by Mark Davies. Future devices should added to the MyDevices portal <https://mydevices.wgtn.ac.nz/> (staff login required).

The current WiFi network status is:

```shell
pi@HTL:~ $ wpa_cli -i wlan0 status
bssid=ac:4a:56:c2:d6:a3
freq=2462
ssid=WellingtonUniversityGuest
id=0
mode=station
pairwise_cipher=NONE
group_cipher=NONE
key_mgmt=NONE
wpa_state=COMPLETED
ip_address=10.140.153.132
p2p_device_address=02:c4:dc:2d:e0:be
address=b8:27:eb:8f:6c:96
uuid=55201e7d-f982-5977-b32c-ee53f10046d5
```

### Bash

The file [bashrc](files/bashrc) has some small additions to the defaults for making the Bash history easier to work with:

```shell
pi@HTL:~ $ diff .bashrc .bashrc~
19,22c19,20
< HISTSIZE=2000
< HISTFILESIZE=8000
< HISTTIMEFORMAT="%F %T "       # Timestamp.
< PROMPT_COMMAND="history -a"   # Write to HISTIFLE immediately
---
> HISTSIZE=1000
> HISTFILESIZE=2000
```

### gitlab-runner

It appears that `gitlab-runner` on Debian OS's create a new user `gitlab-runner` and the runner is installed and runs on the system, rather than in the user space as on macOS. The `config.toml` file is thus stored in `/etc/gitlab-runner/config.toml` and is readable only by `root`:

```shell
pi@HTL:~ $ sudo ls -al /etc/gitlab-runner/
total 12
drwx------   2 root root 4096 Jul 27  2020 .
drwxr-xr-x 116 root root 4096 Nov 11 14:17 ..
-rw-------   1 root root  297 Jul 27  2020 config.toml
```

### ssh

The file `sshd_config` disables password authentication and allows public key authentication and needs to be copied to `/etc/ssh`. The host keys also potentially need to be part of the provisioning of the build & test server but will need to be stored securely in the repo. The contents of `/etc/ssh/` are:

```shell
pi@HTL:~ $ sudo ls -l /etc/ssh/
total 584
-rw-r--r-- 1 root root 553122 Mar  2  2018 moduli
-rw-r--r-- 1 root root   1723 Mar  2  2018 ssh_config
-rw-r--r-- 1 root root   3296 Apr 21  2021 sshd_config
-rw------- 1 root root    672 Mar 14  2018 ssh_host_dsa_key
-rw-r--r-- 1 root root    606 Mar 14  2018 ssh_host_dsa_key.pub
-rw------- 1 root root    227 Mar 14  2018 ssh_host_ecdsa_key
-rw-r--r-- 1 root root    178 Mar 14  2018 ssh_host_ecdsa_key.pub
-rw------- 1 root root    411 Mar 14  2018 ssh_host_ed25519_key
-rw-r--r-- 1 root root     98 Mar 14  2018 ssh_host_ed25519_key.pub
-rw------- 1 root root   1675 Mar 14  2018 ssh_host_rsa_key
-rw-r--r-- 1 root root    398 Mar 14  2018 ssh_host_rsa_key.pub`
```

---
