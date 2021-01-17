registry = []

def register(func):
    print('running register (%s)'%func)
    registry.append(func)
    return func


@register
def f1():
    print('f1() is running')

@register
def f2():
    print('f2() is running')

def f3():
    print('f3 is running')

