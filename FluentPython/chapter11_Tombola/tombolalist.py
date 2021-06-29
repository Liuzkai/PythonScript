# 使用注册的方法来实现虚拟子类有两种方法：一个是使用修饰器，一个是使用register函数
import sys
sys.path.extend(r'/Users/liuzhongkai/Documents/Git/PythonScript/FluentPython/chapter11_Tombola/')

from random import randrange
from tombola import Tombola

# 使用第一种方法
@Tombola.register  # 使用基类的register修饰器来创建虚拟子类
class TombolaList(list):    # 实际继承了list类，亦可称为对list类的扩展

    # def __init__(self):   # 直接继承list，不需要重新实现初始化方式

    # 下面需要实现抽象基类的说有方法：
    def pick(self):         # 这里直接使用了list的__bool_方法
        if self:              
            index = randrange(len(self))
            return self.pop(index)
        else:
            raise LookupError("pick from empty TombolaList!")

    load = list.extend # 注意！这里直接将list的extent方法赋值给了虚拟子函数，因为他们的功能是一样的，省去了重新定义！！！
    # load = self.extend # 不能使用self.extend,会返回错误：name 'self' is not defined
                         # 而且在逻辑上也是不对的，毕竟self是该子函数，而不是父类。

    def loaded(self):
        return bool(list)

    def inspect(self):
        return tuple(sorted(self))
