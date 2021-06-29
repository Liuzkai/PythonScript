# 另一个子类：覆盖抽象类中的非抽象方法，提高效率
import sys
sys.path.extend(r'/Users/liuzhongkai/Documents/Git/PythonScript/FluentPython/chapter11_Tombola/')

import random
from tombola import Tombola

class LotterBlower(Tombola):

    def __init__(self, iterable):
        self._ball = list(iterable) # 这里用到了4.2的方法，创建一个副本，避免使用传入的序列，产生混淆。（尤其是我们的类还要删除和增添该数组）

    def load(self, iterable):
        self._ball.extend(iterable)

    def pick(self):
        try:
            index = random.randrange(len(self._ball))
        except ValueError:
            raise LookupError("pick from empty LotterBlower!")
        return self._ball.pop(index)

    # 覆盖重构抽象类中已经实现的非抽象方法，来提高函数效率。
    def loaded(self):
        return bool(self._ball)

    # 覆盖重构抽象类中已经实现的非抽象方法，来提高函数效率。
    def inspect(self):
        return tuple(sorted(self._ball))