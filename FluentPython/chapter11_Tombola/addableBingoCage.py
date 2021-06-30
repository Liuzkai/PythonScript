import sys
sys.path.append(r"D:\UGit\PythonScript\FluentPython\chapter11_Tombola")
import random
from tombola import Tombola


class AddableBingoCage(Tombola):

    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')

    def __add__(self, other):
        if isinstance(other, Tombola):
            return AddableBingoCage(self.inspect() + other.inspect())   # 操作符需要返回一个新对象
        else:
            return NotImplemented

    # 增量赋值操作符
    def __iadd__(self, other):
        if isinstance(other, Tombola):
            other_iterable = other.inspect()
        else :
            try:
                other_iterable = iter(other)
            except TypeError:
                self_cls = type(self).__name__
                msg = "right operand in += must be {!r} or an iterable".format(self_cls)
                raise TypeError(msg)
        self.load(other_iterable)
        return self # 增量赋值运算必须返回自己！

    def __call__(self):
        self.pick()