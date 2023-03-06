# Data Recorder webapp build and deploy using GNU Make
#
# Build: runs `npm run build` which automatically creates an output
# directory `build`; creates a directory `static` and creates
# compressed output in that directory for deployment.
#
# Deploy: Uploads the files in the `build/static` directory to the
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
STATICDIR := build/static
# Dataloss Warning: REMOTE is used with the `rshell rsync --mirror`
# command below. REMOTE _must never_ resolve to the top-level
# `/pyboard/` directory, if it does then `rsync --mirror` will delete
# all files and directories from the top level which do not appear in
# the source directory resulting in dataloss.
REMOTE := /datarecorder/static

# Set variables for lists of subdirectories of SRCDIR.
#
# GNU Make Manual References:
#   Section 8.13 The shell Function
#
SRCDIRS := $(shell find $(SRCDIR) -type d)

# Set variables for source, object and remote file lists. These are
# used in the target and prerequisite rules.
#
# For the webapp all `.tsx`, `.css`, `.ico`, `.png` and `.svg` files
# in subdirectories are sources for `preact build`, i.e. are build
# prerequisites.
#
# GNU Make Manual References:
#   Section 4.4 Using Wildcard Characters in File Names
#   Section 4.4.2 Pitfalls of Using Wildcards
#   Section 4.4.3 The Function `wildcard`

# Sources
#
SRCEXTS := *.tsx *.css *.ico *.png *.svg

SOURCES := $(foreach ext,$(SRCEXTS),$(foreach srcdir,$(SRCDIRS),$(wildcard $(srcdir)/$(ext))))

# Objects
#
# Preact build creates object files with hashes, so use wildcards when
# specifying the object files. Note:
#
#    "Wildcard expansion does not happen when you define a variable...
#    if you use the value of objects in a target or prerequisite,
#    wildcard expansion will take place there. If you use the value of
#    objects in a recipe, the shell may perform wildcard expansion
#    when the recipe runs"
#
# GNU Make Manual References:
#   Section 4.4 Using Wildcard Characters in File Names
#   Section 4.4.2 Pitfalls of Using Wildcards
#

# Use the index.html file as the sentinel file (see below)
OBJECTS := $(OUTDIR)/index.html
STATICFILES := $(STATICDIR)/index.html.gz

# The hidden lockfile can be used as a "sentinel" file for Make to
# determine whether the `node_modules` require updating. The hidden
# lockfile is created by npm 7 and above and using it thus adds an npm
# version requirement to the build. see:
# <https://docs.npmjs.com/cli/v7/configuring-npm/package-lock-json#hidden-lockfiles>.
NODE_MODULES := node_modules/.package-lock.json

# Set a variable for the build information file which is copied to the
# ESP32 flash memory to indicate the deployed software revision.
#
BUILDINFO := $(STATICDIR)/BUILD.json


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
.PHONY: all node build static clean clean-static deep-clean upload uninstall repl
#
# Note: the output of entire targets can be muted with the special
# target `.SILENT`. Example:
.SILENT: clean clean-static  deep-clean

#: Install Node modules and build static webapp files
all: static

#: Install or update required Node modules
node: $(NODE_MODULES)

#: Run 'preact build' via the npm build script
build: $(OBJECTS)

#: Create a static copy of the webapp for deployment
static: $(STATICFILES)

#: Deletes all files that are normally created by `remake`
clean:
	-rm -rf $(OUTDIR)/*

#: Deletes the webapp static files only
clean-static:
	-rm -rf $(STATICDIR)/*

#: Deletes the entire build directory and all files
deep-clean:
	-rm -rf $(OUTDIR)

#: An alias for `upload`
install: upload

#: Upload the webapp files to a connected data recorder
# Dataloss Warning: use of `rshell rsync --mirror` is required because
# each revised build of the webapp has a different hash in the
# `bundle.<hash>...` files and the old version should be removed.
# Strictly only the static directory should be the remote target
# otherwise other files and directories will be deleted. This
# potentially includes the contents of the microSD card if it is
# mounted at the time of synchronisation.
upload: static
	rshell --port $(PORT) --baud $(BAUD) \
		rsync --mirror ./$(STATICDIR) $(REMOTE)

#: Deletes webapp files from a connected data recorder
uninstall:
	rshell --port $(PORT) --baud $(BAUD) \
		rm -rf $(REMOTE)/*

#: Simple alias to open a REPL connection
repl:
	rshell --port $(PORT) --baud $(BAUD) repl


# Ordinary Rules
#
# An "ordinary rule" has an explicitly specified file as its target
# (cf. pattern rules, below). The rules for building the webapp are
# defined in a top-down manner below, but keep in mind that Make
# executes the recipes specified in the rules from the bottom-up.
#
# Creation of the set of static files is the goal of the build, the
# following rule defines the dependency relationship between the
# static files and the object files created by `npm run build`. An
# order-only prerequisite is used to ensure that the `build/static`
# directory exists before attempting to copy the static files.
#
# Note: The version of gzip in the Alpine Linux Docker image does not
# support the `--keep` option, only `-k`.
#
# GNU Make Manual References:
#   Section 4.3 Types of Prerequisites
#
$(STATICFILES) : $(OBJECTS) | $(STATICDIR)
	gzip -k $< $(OUTDIR)/bundle.*.css $(OUTDIR)/bundle.*.esm.js
	cp $(OUTDIR)/*.gz $(STATICDIR)/ && rm -f $(OUTDIR)/*.gz
	cp $(OUTDIR)/assets/favicon.ico $(STATICDIR)/
	cp $(OUTDIR)/assets/icons/apple-touch-icon.png $(STATICDIR)/
	@printf '{"sha": "%s", "built_at": "%s", "clean": %s }\n' \
		"$$(git rev-parse HEAD)" "$$(date "+%Y-%m-%d %H:%M")" \
		$$(if [[ -z "$$(git status $(SRCDIR) --porcelain --untracked-files=no)" ]] ; \
		then echo "true" ; else echo "false" ; fi ) > $(BUILDINFO)

$(STATICDIR):
	mkdir $(STATICDIR)

# Create the webapp object files with `npm run build`, a one-line
# script defined in `package.json` which needs to be run:
# - when the source files ( TypeScript, CSS, etc.) are more recent
#   than the object files;
# - when any of the object files don't exist
# `npm run build` should be run _once only_, not once for each of the
# object files, so use the build info file as a "sentinel" file.
#

# The rule below tells Make to create the OBJECT files if they do not
# exist and to update them if any of the sources or Node modules are
# newer than the OBJECT files. Note that the recipe will be executed
# for each of the OBJECT files, so because `npm run build` creates all
# files OBJECTS must be a single file only. Use `index.html` as the
# sentinel file.
#
$(OBJECTS) : $(SOURCES) $(NODE_MODULES)
	npm run build

# Install the Node modules required by the webapp.
#
# The hidden lockfile `node_modules/.package-lock.json` is used as a
# "sentinel" file for Make to determine whether the `node_modules`
# require updating: `npm install` needs to be run only when the
# webapp's `package.json` file is newer than the hidden lockfile. This
# file is created by npm 7 and above and using it thus adds a version
# requirement of npm 7 or later to the build.
# <https://docs.npmjs.com/cli/v7/configuring-npm/package-lock-json#hidden-lockfiles>.
#
# As the top-level `package-lock.json` file is (appropriately) also
# under version control and is modified by npm 7 and above, this is
# also a Node modules prerequisite.
#
$(NODE_MODULES) : package.json package-lock.json
	npm install --legacy-peer-deps
