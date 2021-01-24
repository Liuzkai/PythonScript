import time
import functools


'''
示例0中实现的 clock 装饰器有几个缺点:不支持关键字参数，
而且遮盖了被装饰函数的 __name__ 和 __doc__ 属性。本示例使用
functools.wraps 装饰器把相关的属性从 func 复制到 clocked 中。
此外，这个新版还能正确处理关键字参数。
'''
def clock(func):

    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        arg_list = []
        if args:
            arg_list.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s = %r'%(k, w) for k, w in sorted(kwargs.items())]
            arg_list.append(pairs)
        arg_str = ', '.join(arg_list)
        print("[%0.8fs] %s(%s) -> %r" %(elapsed, name, arg_str, result))
        return result

    return clocked

