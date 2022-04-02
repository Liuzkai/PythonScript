# 基础知识汇总

# 类与继承
class Student(object):
    def __init__(self, name, score):
        self.name = name
        self.__score = score  #前面加两个下划线，变量就变成私有变量


'''
需要注意的是，在Python中，变量名类似__xxx__的，也就是以双下划线开头，并且以双下划线结尾的，是特殊变量，特殊变量是可以直接访问的，不是private变量，所以，不能用__name__、__score__这样的变量名。

有些时候，你会看到以一个下划线开头的实例变量名，比如_name，这样的实例变量外部是可以访问的，但是，按照约定俗成的规定，当你看到这样的变量时，意思就是，“虽然我可以被访问，但是，请把我视为私有变量，不要随意访问”。

双下划线开头的实例变量是不是一定不能从外部访问呢？其实也不是。不能直接访问__name是因为Python解释器对外把__name变量改成了_Student__name，所以，仍然可以通过_Student__name来访问__name变量：

但是强烈建议你不要这么干，因为不同版本的Python解释器可能会把__name改成不同的变量名。

总的来说就是，Python本身没有任何机制阻止你干坏事，一切全靠自觉。
'''



    def printStudent(self):
        print(self.name)

# 和静态语言不同，Python允许对实例变量绑定任何数据，也就是说，对于两个实例变量，虽然它们都是同一个类的不同实例，但拥有的变量名称都可能不同：
jam = Student('jam', 87)
jam.age = 18 #age是类中没有的变量，但是我们可以给实例绑定该值，其他实例是没有的。


#继承和多态
class Animal(object):   #编写Animal类
    def run(self):
        print("Animal is running...")

class Dog(Animal):  #Dog类继承Amimal类，没有run方法
    pass

class Cat(Animal):  #Cat类继承Animal类，有自己的run方法
    def run(self):
        print('Cat is running...')
    pass

class Car(object):  #Car类不继承，有自己的run方法
    def run(self):
        print('Car is running...')

class Stone(object):  #Stone类不继承，也没有run方法
    pass

def run_twice(animal):
    animal.run()
    animal.run()

run_twice(Animal())
run_twice(Dog())
run_twice(Cat())
run_twice(Car())
run_twice(Stone())

'''
def run_twice(animal)

虽然参数的名字为animal，但是python并不能限制它是Animal类型的变量，这个变量名字即使为a，为b都可以，所以在执行方法时，调用的是这个变量的run方法，所以 只要有run方法都可以成功。

所以对于下面的话，也是因为静态语言对参数做了限制，如果python在函数体里使用isinstance(animal, Animal)做判断也可以起到静态语言的效果。

对于静态语言（例如Java）来说，如果需要传入Animal类型，则传入的对象必须是Animal类型或者它的子类，否则，将无法调用run()方法。

对于Python这样的动态语言来说，则不一定需要传入Animal类型。我们只需要保证传入的对象有一个run()方法就可以了

这就是动态语言的“鸭子类型”，它并不要求严格的继承体系，一个对象只要“看起来像鸭子，走起路来像鸭子”，那它就可以被看做是鸭子。

Python的“file-like object“就是一种鸭子类型。对真正的文件对象，它有一个read()方法，返回其内容。但是，许多对象，只要有read()方法，都被视为“file-like object“。许多函数接收的参数就是“file-like object“，你不一定要传入真正的文件对象，完全可以传入任何实现了read()方法的对象。

'''


# 类型判断

type(123)==int
#True

# 判断方法：
import types

type(fn)==types.FunctionType
# True
type(abs)==types.BuiltinFunctionType
# True
type(lambda x: x)==types.LambdaType
# True
type((x for x in range(10)))==types.GeneratorType
# True

# 能用type()判断的基本类型也可以用isinstance()判断：
#  总是优先使用isinstance()判断类型，可以将指定类型及其子类“一网打尽”。

isinstance('a', str)
# True
isinstance(123, int)
# True
isinstance(b'a', bytes)
# True

# 使用dir()
# 如果要获得一个对象的所有属性和方法，可以使用dir()函数，它返回一个包含字符串的list，比如，获得一个str对象的所有属性和方法：
dir('ABC')
#['__add__', '__class__',..., '__subclasshook__', 'capitalize', 'casefold',..., 'zfill']