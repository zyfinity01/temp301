#!/bin/bash

ls
cd ./device/src || exit
export MICROPYPATH=./device/src/lib
/micropython/ports/unix/micropython -c "import tricolor" || echo "no bueno"
/micropython/ports/unix/micropython -c "import unittest; unittest.main('test/test_docker')"
