from drivers import sdcard

import os
import time

sdcard.setup()


def test(func, count, iter_):
    total = 0
    for i in range(iter_):
        out = func(count)
        print("Test {} took {} ns".format(i, out))
        total += out
    print("Total time: {}".format(total))
    print("Average time: {}".format(total / iter_))


def test_write(iterations):
    print("Beginning test")
    start_time = time.time_ns()
    with open(sdcard.gen_path("DELETE.FILE"), "w+") as f_ptr:
        for i in range(iterations):
            f_ptr.write("H" * 999 + "\n")
    end_time = time.time_ns()
    os.remove(sdcard.gen_path("DELETE.FILE"))
    return end_time - start_time


def test_readwrite(iterations):
    print("Initialising test file, please wait")
    with open(sdcard.gen_path("DELETE.FILE"), "w+") as f_ptr:
        for i in range(iterations):
            f_ptr.write("H" * 999 + "\n")
    print("file initialised, beginning test")

    start_time = time.time_ns()
    with open(sdcard.gen_path("DELETE.FILE"), "r") as r_ptr:
        with open(sdcard.gen_path("DELETE_TMP.FILE"), "w+") as f_ptr:
            for line in r_ptr:
                f_ptr.write(line)

    end_time = time.time_ns()
    os.remove(sdcard.gen_path("DELETE.FILE"))
    os.remove(sdcard.gen_path("DELETE_TMP.FILE"))
    return end_time - start_time


def test_read(iterations):
    print("Initialising test file, please wait")
    with open(sdcard.gen_path("DELETE.FILE"), "w+") as f_ptr:
        for i in range(iterations):
            f_ptr.write("H" * 999 + "\n")
    print("file initialised, beginning test")

    start_time = time.time_ns()
    output = ""
    with open(sdcard.gen_path("DELETE.FILE"), "r") as r_ptr:
        for line in r_ptr:
            output = line

    end_time = time.time_ns()
    os.remove(sdcard.gen_path("DELETE.FILE"))
    print(output)
    return end_time - start_time
