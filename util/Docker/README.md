# Docker Images for CI Runner

<!--
[TOC]
-->

## Lint Stage

**Purpose:** to have a Docker image optimised for linting on the CI pipeline.

### pre-commit and Ruby

Don't install pre-commit via `apt-get` because it gives an older version as well as about 250 MB of dependencies... that aren't really needed.

Do need to install ruby because pre-commit will fail on installation of markdownlint with a "Executable `gem` not found" error.

**Note:** didn't think this was supposed to happen, but it's apparently normal behaviour for pre-commit according to <https://github.com/pre-commit/pre-commit/issues/1930>.

## Docker Image for LaTeX Typesetting

**Purpose:** to have the latest TeX Live distribution containerised for automatic typesetting of LaTeX files on the continuous integration pipeline.

### Installation from CTAN

This is the preferred method because it allows the latest release to be installed _and_ the structure is not modified by a package manager (`apt` appears to change the install location and breaks TeX Live's internal update mechanisms).

#### Automatic Verification Using gpg

In order for `install-tl` and `tlmgr` to be able to verify the packages, `gpg` must be present. Integrity checking of the packages is crucial because the automated CI pipeline will fail if any packages have been corrupted.

### Perl, Python and Ruby

Only install `perl` and not `python` or `ruby`, in an attempt to minimise the image size. Note, however, that some of the scripts in `texmf-dist/scripts` use Python and Ruby

```shell
root@66337a396b99:/usr/local/texlive/2021/texmf-dist/scripts# egrep -hIr "^\#\!" . | sort | uniq -c | sort -r
    [Edited]
    98 #!/usr/bin/env perl
    84 #!/bin/sh
    30 #!/usr/bin/env python
    12 #!/usr/bin/env ruby
```

## Dockerfile Construction Notes

### Time Zone Settings

Set the timezone `TZ` environment variable and `apt-get install` the `tzdata` package to prevent interactive questions when git is installed. Note: the `TZ` environment variable persists at runtime <https://serverfault.com/questions/949991/how-to-install-tzdata-on-a-ubuntu-docker-image>. Found it necessary to execute the

```shell
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

command to have the `date` command and various logs report the correct local date and time.

### `apt-get install`

Added apt-utils to the `apt-get install` block to suppress/avoid the following warnings:

```shell
debconf: unable to initialize frontend: Dialog
```

Might need to install 'dialog' also according to the advice in <https://github.com/moby/moby/issues/27988>.

Could use the `--no-install-recommends` flag to save, at most, a few 10's of MB but as the `scheme-full` installation is nearly 4 GB, it doesn't seem worth the risk of omitting recommended packages.

### Docker Image Size Minimisation

#### TeX Live

Want to minimise the image size. The `blang/latex` image is 4.3 GB in size!. There is a huge difference between `scheme-basic` and `scheme-full`.

The `scheme-basic` Docker image is 648 MB with the default `install-tl` options. The installation takes 234 MB of which 146 MB (62%) is taken by documentation and source files.

```bash
root@6550686aac24:~# du -shc /usr/local/texlive/2021/texmf-dist/* | egrep "M" | sort -nr
128M    /usr/local/texlive/2021/texmf-dist/doc
59M     /usr/local/texlive/2021/texmf-dist/fonts
27M     /usr/local/texlive/2021/texmf-dist/tex
18M     /usr/local/texlive/2021/texmf-dist/source
1.3M    /usr/local/texlive/2021/texmf-dist/scripts
...
234M    total
```

As detailed in the `install-tl` documentation, these can be omitted on install by setting `tlpdbopt_install_docfiles 0` and `tlpdbopt_install_srcfiles 0` at install time. The `tlmgr` man page indicates that these can be restored by using the flags `--with-doc` and `--with-src` in conjunction with `--reinstall`.

Not installing documentation and source doesn't save as much space as was expected from tests on `scheme-basic` because most of the additional 3.4 GB of space is consumed by fonts:

```shell
2.7G    /usr/local/texlive/2021/texmf-dist/fonts
491M    /usr/local/texlive/2021/texmf-dist/tex
123M    /usr/local/texlive/2021/texmf-dist/scripts
 35M    /usr/local/texlive/2021/texmf-dist/tex4ht
 24M    /usr/local/texlive/2021/texmf-dist/bibtex
 13M    /usr/local/texlive/2021/texmf-dist/source
7.3M    /usr/local/texlive/2021/texmf-dist/dvips
6.8M    /usr/local/texlive/2021/texmf-dist/doc
5.4M    /usr/local/texlive/2021/texmf-dist/metapost
3.8M    /usr/local/texlive/2021/texmf-dist/xindy
3.8M    /usr/local/texlive/2021/texmf-dist/ls-R
2.6M    /usr/local/texlive/2021/texmf-dist/context
2.5M    /usr/local/texlive/2021/texmf-dist/asymptote
2.1M    /usr/local/texlive/2021/texmf-dist/omega
```

A comparison of no-documentation no-source installation Docker images is

| Tex Live Scheme | Docker Image Size |
| --- | --- |
| `scheme-basic` | 281 MB |
| `scheme-full` | 3.73 GB |
| `blang/latex` | 4.33 GB |

### Ubuntu

While `blag/latex` installs `build-essential` and `wget` in order to build and install TeX Live, these tools combined take 291 MB and (possibly) aren't used again.

```shell
root@3cd9bc8d67e8:/# apt-get remove build-essential wget
...
root@3cd9bc8d67e8:/# apt-get autoremove
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages will be REMOVED:
  binutils binutils-common binutils-x86-64-linux-gnu bzip2 cpp cpp-10 dirmngr
  dpkg-dev fakeroot g++ g++-10 gcc gcc-10 gcc-10-base gnupg gnupg-l10n
  gnupg-utils gpg gpg-agent gpg-wks-client gpg-wks-server gpgconf gpgsm
  libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl
  libasan6 libasn1-8-heimdal libassuan0 libatomic1 libbinutils libbsd0
  libc-dev-bin libc-devtools libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0
  libctf0 libdeflate0 libdpkg-perl libfakeroot libfile-fcntllock-perl
  libgcc-10-dev libgd3 libgdbm-compat4 libgdbm6 libgomp1 libgssapi3-heimdal
  libhcrypto4-heimdal libheimbase1-heimdal libheimntlm0-heimdal
  libhx509-5-heimdal libisl23 libitm1 libjbig0 libjpeg-turbo8 libjpeg8
  libkrb5-26-heimdal libksba8 libldap-2.4-2 libldap-common
  liblocale-gettext-perl liblsan0 libmd0 libmpc3 libmpfr6 libnpth0 libnsl-dev
  libperl5.32 libpsl5 libquadmath0 libreadline8 libroken18-heimdal libsasl2-2
  libsasl2-modules libsasl2-modules-db libsqlite3-0 libstdc++-10-dev libtiff5
  libtirpc-dev libtsan0 libubsan1 libwebp6 libwind0-heimdal libx11-6
  libx11-data libxau6 libxcb1 libxdmcp6 libxpm4 linux-libc-dev
  lto-disabled-list make manpages manpages-dev netbase patch perl
  perl-modules-5.32 pinentry-curses publicsuffix readline-common rpcsvc-proto
  xz-utils
0 upgraded, 0 newly installed, 105 to remove and 0 not upgraded.
After this operation, 291 MB disk space will be freed.
Do you want to continue? [Y/n]
```

## Docker Image Build Notes

Build the Docker images for the container registry with (from
<https://gitlab.ecs.vuw.ac.nz/course-work/engr301/2023/group<n>/data-recorder/container_registry>)

```shell
docker login gitlab.ecs.vuw.ac.nz:45678
docker build -t gitlab.ecs.vuw.ac.nz:45678/course-work/engr301/2023/group<n>/data-recorder .
docker push gitlab.ecs.vuw.ac.nz:45678/course-work/engr301/2023/group<n>/data-recorder
```

Had a problem using `docker login ...` over ssh and with tmux on macOS. The fix [1] is to unlock the keychain:

```shell
$ docker login gitlab.ecs.vuw.ac.nz:45678
Username: •••
Password:
Error saving credentials: error storing credentials - err: exit status 1, out: `error storing credentials - err: exit status 1, out: `User interaction is not allowed.``
$ security unlock-keychain
password to unlock default:
$ docker login gitlab.ecs.vuw.ac.nz:45678
Authenticating with existing credentials...
Login Succeeded
```

The macOS Keychain status can be shown with `security show-keychain-info` and confirms the initial error message. Speculation from [1] is that a modal GUI dialog is displayed which is inaccessible across ssh.

```shell
$ security show-keychain-info
security: SecKeychainCopySettings <NULL>: User interaction is not allowed.
$ security unlock-keychain
password to unlock default:
$ security show-keychain-info
Keychain "<NULL>" no-timeout
```

1. Docker login not possible on remote Mac (Error saving credentials) <https://memotut.com/en/af6adef956b4447c90c2/>

---
