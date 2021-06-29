# 对子类的自动化测试
# 技术：doctest

import sys
sys.path.extend(r'/Users/liuzhongkai/Documents/Git/PythonScript/FluentPython/chapter11_Tombola/')

import doctest
from tombola import Tombola
import bingocage, lotterblower, tombolalist

import abc

abc.ABCMeta.__subclasscheck__()

TEST_FILE = 'tombola_tests.rst'
MSG = "{0:16} {1.attemped:2} tests, {1.failed:2} failed - {2}"

def main(avgv):
    verbose = '-v' in avgv
    real_subclasses = Tombola.__subclasses__()
    virtual_subclasses = list(Tombola._abc_registry)
    for cls in real_subclasses + virtual_subclasses:
        test(cls, verbose)


def test(cls, verbose = False):
    res = doctest.testfile(
        TEST_FILE,
        globs={'ConcreteTombola':cls},
        verbose = verbose,
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

    tag = 'Failed' if res.failded else "Ok"
    print(MSG.format(cls.__name__,res,tag))

if __name__ == '__main__':
    main(sys.argv)

    
