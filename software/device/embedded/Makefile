# Copyright (C) 2023  Benjamin Secker, Jolon Behrent, Louis Li, James Quilty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Data Recorder embedded software build and deploy using GNU Make
#
# Build: compiles `.py` files from a source directory hierarchy into
# `.mpy` files in an output directory hierarchy using mpy-cross.
#
# Deploy: Uploads the files in the output directory hierarchy to the
# data recorder's flash memory.
#
# References
# 1. GNU Make Manual <https://www.gnu.org/software/make/manual/make.html>
# 2. Peter Miller "Recursive MakeConsidered Harmful", AUUGN 19, 14 (1997)
#    <https://grosskurth.ca/bib/1997/miller.pdf>

ifeq ($(OS),Windows_NT)
	$(error unable to build the embedded software on Microsoft Windows.)
endif

# Variables Section
#
# Always use immediate evaluation assignment (`:=`) unless deferred
# evaluation is required [Ref. 2, secton 5.2].
#
# GNU Make Manual References:
#   Section 2.4 Variables Make Makefiles Simpler
#   Section 3.7 How make Reads a Makefile
#   Section 6.2 The Two Flavors of Variables

# Set variables required for connection to the Data Recorder's
# ESP32 microcontroller via USB using rshell.
#
# The PORT name differs between macOS and Linux, try to detect the
# operating system name and set the default PORT string. Note that if
# multiple devices are connected by USB on Linux the data recorder
# port may be `/dev/ttyUSB1` or `/dev/ttyUSB2`, etc.
#
# If the SHELL variable is not set in the Makefile then /bin/sh is
# used. macOS aliases /bin/sh to /bin/bash but Linux actually runs sh
# and will raise errors on recipes that function on macOS. Set SHELL
# to /bin/bash to avoid this problem.
#
# GNU Make Manual References:
#   Section 7 Conditional Parts of Makefiles
#   Section 8.13 The shell Function
#
BAUD := 115200
SHELL := /bin/bash
UNAME := $(shell uname -s)
ifeq ($(UNAME),Darwin)
	PORT := /dev/cu.SLAB_USBtoUART
endif
ifeq ($(UNAME),Linux)
	PORT := /dev/ttyUSB0
endif

# Set variables for the various directory base names used in building
# and deploying the embedded software. These are subsequently used in
# variables and rules defining targets and prerequisites.
#
SRCDIR := src
OUTDIR := build
REMOTE := /datarecorder

# Set variables for lists of subdirectories of SRCDIR.
#
# GNU Make Manual References:
#   Section 8.13 The shell Function
#
SRCDIRS := $(shell find $(SRCDIR) -type d)

# Create a list of output directories matching the source directory
# hierarchy using a substitution reference. This list is used to
# ensure that the output directories exist prior to running mpy-cross:
# compilation fails silently if the output directory does not exist.
#
# GNU Make Manual References:
#   6.3.1 Substitution References
#
OUTDIRS := $(SRCDIRS:$(SRCDIR)%=$(OUTDIR)%)

# Create the `rshell rsync --mirror` commands required for the
# `upload-mirror` deploy target.
#
# Note: Mirroring is a destructive operation and requires careful
# construction of the OUTDIR sub-directory list to be synchronised
# with the corresponding directories in the ESP32 flash memory.
#
# Dataloss Warning: `rshell rsync --mirror <localdir> /pyboard/` will
# delete the contents of the microSD card if it is mounted at the time
# of synchronisation. As a precaution the top level of the output
# directory is not included in RSYNCDIRS.
#
# GNU Make Manual References:
#   Section 8.5 The foreach Function
#
RSYNCDIRS := $(shell find $(SRCDIR) -mindepth 1 -maxdepth 1 -type d)
RSYNCDIRS := $(RSYNCDIRS:$(SRCDIR)/%=%)
RSYNC := $(foreach subdir,$(RSYNCDIRS),rsync --mirror ./$(OUTDIR)/$(subdir) $(REMOTE)/$(subdir) \;)

# Set variables for source, object and remote file lists. These are
# used in the target and prerequisite rules.
#
# For the MicroPython code we want all `.py` files in subdirectories
# to be compiled with mpy-cross _but_ we need the `boot.py` and
# `main.py` files at the top level to remain uncompiled because
# `boot.mpy` and `main.mpy` are not recognised by MicroPython v 1.14.
#
# Create a list of `.py` and `.mpy` objects based on the source file
# list. The pattern rules for `.mpy` and `.py` targets, defined below,
# is then be applied to the object list to create the specified set
# of files in the output directory.
#
# The list of `.mpy` objects is everything in the source directory
# which has a `.py` suffix.
#
# GNU Make Manual References:
#   Section 4.4 Using Wildcard Characters in File Names
#   Section 4.4.2 Pitfalls of Using Wildcards
#   Section 4.4.3 The Function `wildcard`
#
SOURCES := $(foreach srcdir,$(SRCDIRS),$(wildcard $(srcdir)/*.py))

# Create the list of object files, where the boot.py and main.py files
# at the top level are a special case because they are not recognised
# by MicroPython if they are `.mpy` compiled bytecode. The boot.py and
# main.py object files are plain Python.
#
OBJECTS := $(SOURCES:$(SRCDIR)/%.py=$(OUTDIR)/%.mpy)
OBJECTS := $(subst $(OUTDIR)/board.mpy,$(OUTDIR)/board.py,$(OBJECTS))
OBJECTS := $(subst $(OUTDIR)/boot.mpy,$(OUTDIR)/boot.py,$(OBJECTS))
OBJECTS := $(subst $(OUTDIR)/main.mpy,$(OUTDIR)/main.py,$(OBJECTS))

# The list of remote files on the data recorder is the list of object
# files with the data recorder mount point as the directory root.
REMOTES := $(OBJECTS:$(OUTDIR)/%=$(REMOTE)/%)

# Set a variable for the build information file which is copied to the
# ESP32 flash memory to indicate the deployed software revision.
#
BUILDINFO := $(OUTDIR)/BUILD.json


# Rules Section
#
# Rules have the form:
#
#   target … : prerequisites …
#       recipe
#
# The order of rules in the Makefile determines which rule is
# considered the default goal. The default goal is the target of the
# _first_ rule in the Makefile: if no target is specified on the
# command line then Make uses the target of the first rule.
#
# By convention Makefiles are written with the first rule specifying a
# target `all` which builds everything. Rules whose targets are not
# the names of files are called "phony targets" in the manual and
# specify actions.
#
# GNU Make Manual References:
#   Section 2.1 What a Rule Looks Like
#   Section 4 Writing Rules
#   Section 4.6 Phony Targets
#

# Actions
#
# Group all actions (rules with "phony targets") as a single
# block with the first rule `all` becoming the default goal. Good
# practice is to explicitly specify all phony targets with the
# built-in target name `.PHONY`.
#
# By default, Make echoes recipe lines during execution. Recipe lines
# can be "muted" by prefixing the command with the single character
# `@`. To ignore errors in a recipe line, prefix the command with the
# single character `-`. Prefixes can be combined.
#
# GNU Make Manual References:
#   Section 4.9 Special Built-in Target Names
#   Section 5.2 Recipe Echoing
#   Section 5.5 Errors in Recipes
#
.PHONY: all clean upload upload-mirror upload-src erase-upload uninstall uninstall-src repl
#
# Note: the output of entire targets can be muted with the special
# target `.SILENT`. Example:
.SILENT: clean deep-clean

#: Default goal: builds embedded code with mpy-cross
all: $(OBJECTS) $(BUILDINFO)

#: Deletes all files that are normally created by `remake`
clean:
	-rm -f $(OBJECTS) $(BUILDINFO)

#: Deletes the entire build directory and all files
deep-clean:
	-rm -rf $(OUTDIR)

#: An alias for `upload`
install: upload

#: Upload the build files to a connected data recorder
upload: $(OBJECTS) $(BUILDINFO)
	rshell --port $(PORT) --baud $(BAUD) \
		rsync ./$(OUTDIR) $(REMOTE)/

#: Strictly mirrors the build subdirectories on the data recorder
#
# Dataloss Warning: `rshell rsync --mirror` will delete files and
# directories from the remote directory which are not found in the
# local directory, potentially including the contents of the microSD
# card if it is mounted at the time of synchronisation. To minimise
# the risk of dataloss, only specified subdirectories are
# synchronised. Consequently, this action will not synchronise files
# at the top level of the output directory, including boot.py and
# main.py.
#
upload-mirror: $(OBJECTS) $(BUILDINFO)
	rshell --port $(PORT) --baud $(BAUD) \
		$(RSYNC)

#: Upload `.py` source files to the data recorder
# This will add `.py` files to any `.mpy` files already on the data
# recorder and potentially give rise to unexpected behaviour. Use the
# `uninstall` and `uninstall-src` actions to purge unwanted files from
# the ESP32.
upload-src:
	rshell --port $(PORT) -b $(BAUD) rsync ./$(SRCDIR) $(REMOTE)/

erase-upload:
	esptool.py --port $(PORT) erase_flash
	esptool.py --chip esp32 --port $(PORT) write_flash --compress 0x1000 \
		~/microPython/esp32spiram-idf4-20210202-v1.14.bin
	rshell --port $(PORT) --baud $(BAUD) \
		rsync ./$(OUTDIR) $(REMOTE)/

#: Deletes build files from a connected data recorder
uninstall:
	rshell --port $(PORT) --baud $(BAUD) \
		rm -f $(REMOTES)

#: Deletes source (.py) files from a connected data recorder
uninstall-src:
	rshell --port $(PORT) --baud $(BAUD) \
		rm -f $(SOURCES:$(SRCDIR)%=$(REMOTE)%)

#: Simple alias to open a REPL connection
repl:
	rshell --port $(PORT) --baud $(BAUD) repl


# Ordinary Rules
#
# An "ordinary rule" has an explicitly specified file as its target
# (cf. pattern rules, below). The rule below tells Make to create the file
# BUILDINFO if it does not exist and to update it if any of the
# OBJECTS are newer than the BUILDINFO file.
#
$(BUILDINFO) : $(OBJECTS)
	@printf '{"sha": "%s", "built_at": "%s", "clean": %s }\n' \
		"$$(git rev-parse HEAD)" "$$(date "+%Y-%m-%d %H:%M")" \
		$$(if [[ -z "$$(git status $(SRCDIR) --porcelain --untracked-files=no)" ]] ; \
		then echo "true" ; else echo "false" ; fi ) > $(BUILDINFO)

# Order-only Prerequisite Rules
#
# Ensure that the output directories exist before attempting to
# mpy-cross compile the source files. See the specific example in
# the GNU Make Manual, Section 4.3 Types of Prerequisites.
#
$(OBJECTS): | $(OUTDIRS)

# Create the directory hierarchy.
#
# In a rule with muliple targets, the automatic variable `$@` is the
# name of whichever target caused the rule's recipe to be run.
#
# GNU Make Manual References:
#   Section 10.5.3 Automatic Variables
#
$(OUTDIRS):
	mkdir $@

# Pattern Rules
#
# Pattern rules use the `%` character to match any nonempty substring
# in the target. The `%` in the prerequisites is the matched string
# from the target. Automatic variable notes:
#
#   '$@' is the file name of the target of the rule.
#   '$<' is the file name of the first prerequisite.
#
# GNU Make Manual References:
#   Section 10.5 Defining and Redefining Pattern Rules
#   Section 10.5.3 Automatic Variables
#
$(OUTDIR)/%.mpy : $(SRCDIR)/%.py
	python3 -m mpy_cross -v -march=xtensawin -o $@ $<

$(OUTDIR)/%.py : $(SRCDIR)/%.py
	cp $< $@

# End of Makefile
