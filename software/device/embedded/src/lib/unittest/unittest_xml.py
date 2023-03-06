import os
import time
import junit_xml
from . import unittest as base
from .unittest import *


def run_class(cls, module, test_result):
    o = cls()
    set_up = getattr(o, "setUp", lambda *_: None)
    tear_down = getattr(o, "tearDown", lambda *_: None)
    # Any arguments passed to unit test run script will be used as a string match filter on tests
    test_filter = sys.argv[1:]
    xml_tests = []

    for name in dir(o):
        if test_filter:
            if not any([(f == name) for f in test_filter]):
                continue
        if name.startswith("test"):
            start = time.time()
            xml_test_case = junit_xml.TestCase(cls.__qualname__)
            print(
                "\n%s%s (%s) ...%s"
                % (bcolors.HEADER, name, cls.__qualname__, bcolors.ENDC),
                end="",
            )
            m = getattr(o, name)
            try:
                set_up(name)
            except TypeError:
                set_up()
            try:
                test_result.testsRun += 1
                m()
                print(bcolors.OKGREEN + " ok" + bcolors.ENDC)
            except SkipTest as e:
                print("%s skipped: %s%s" % (bcolors.WARNING, e.args[0], bcolors.ENDC))
                xml_test_case.add_skipped_info(
                    message=module.__file__, output=e.args[0]
                )
                test_result.skippedNum += 1
            except Exception as ex:
                trace = capture_exc(name, ex)
                test_result.exceptions.append(trace)
                xml_test_case.add_failure_info(message=module.__file__, output=trace)
                print("%s fail in %s: %s%s" % (bcolors.FAIL, name, ex, bcolors.ENDC))
                print(trace)
                test_result.failuresNum += 1
                continue
            finally:
                try:
                    tear_down(name)
                except TypeError:
                    tear_down()
                xml_test_case.elapsed_sec = time.time() - start
                print(xml_test_case.elapsed_sec)
                xml_tests.append(xml_test_case)

    return xml_tests


class TestRunner:
    def run(self, suite):
        xml_tests = []
        res = base.TestResult()
        for c, m in suite.tests:
            xml = run_class(c, m, res)
            xml_tests.extend(xml)

        print("Ran %d tests\n" % res.testsRun)
        if res.failuresNum > 0 or res.errorsNum > 0:
            print(
                base.bcolors.FAIL
                + "FAILED "
                + base.bcolors.ENDC
                + "(failures=%d, errors=%d) " % (res.failuresNum, res.errorsNum)
            )
        else:
            msg = "OK"
            color = base.bcolors.OKGREEN
            if res.skippedNum > 0:
                msg += " (%d skipped)" % res.skippedNum
                color = base.bcolors.WARNING
            print(color + msg + base.bcolors.ENDC)

        return res, xml_tests


def main(module="__main__", noexit=False):
    def test_cases(m):
        for tn in dir(m):
            c = getattr(m, tn)
            if (
                isinstance(c, object)
                and isinstance(c, type)
                and issubclass(c, base.TestCase)
            ):
                yield c

    try:
        m = __import__(module) if isinstance(module, str) else module

    except ImportError as ex:
        print(bcolors.FAIL + "FAILED " + bcolors.ENDC)
        exceptions = [capture_exc(module, ex)]
        ret = -1

    else:
        suite = base.TestSuite()
        for c in test_cases(m):
            suite.addTest((c, m))

        runner = TestRunner()
        result, xml_tests = runner.run(suite)
        exceptions = result.exceptions
        ret = 1 if result.failuresNum else 0

        xml_suite = junit_xml.TestSuite(m.__file__, xml_tests)

        if isinstance(module, str):
            if module == "__main__":
                module = ".".join(
                    sys.argv[0].replace("\\", "/").split("/")[-1].split(".")[0:-1]
                )
                print(module)
        else:
            module = module.__name__

        xml_name = "%s.xml" % module
        with open(xml_name, "wb") as xmlfile:
            try:
                cd = os.getcwd()
            except AttributeError:
                cd = "."
            print("writing xml to %s/%s" % (cd, xml_name))
            junit_xml.to_xml_report_file(xmlfile, [xml_suite])

    if exceptions:
        sep = "\n-------------------------------\n"
        print(sep)
        print(sep.join(exceptions))

    # return non zero return code in case of failures
    if noexit:
        return ret
    sys.exit(ret)


def unittest_all(path=None):
    import uos
    import sys

    def is_file(ftype):
        return ftype == 0x8000

    def is_dir(ftype):
        return ftype == 0x4000

    def run_tests(path):
        for fname, ftype, *_ in uos.ilistdir(path):
            if fname in (".", ".."):
                continue
            fpath = "/".join((path, fname))
            if is_file(ftype):
                if fname.lower().startswith("test_") and fname.endswith(".py"):
                    sys.path.insert(0, str(path))
                    try:
                        modname = fname[0:-3]
                        print("Test detected, module name: {0}".format(modname))
                        main(modname, noexit=True)
                    finally:
                        sys.path.pop(0)
            elif is_dir(ftype):
                run_tests(fpath)

    run_tests(path if path else ".")
