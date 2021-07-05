import re
import reprlib

"""
第二版
实现迭代器
"""

RE_WORD = re.compile('\w+')


class Sentence:

    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __repr__(self):
        return "Sentence(%s)" % reprlib.repr(self.text)

    def __iter__(self):
        return SentenceIterator(self.words)


class SentenceIterator:
"""
    Sentence类的迭代器
"""
    def __init__(self, words):
        self.words = words
        self.index = 0

    # 返回下一个可用的元素，如果没有元素了，抛出 StopIteration异常。
    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return word

    # 返回 self，以便在应该使用可迭代对象的地方使用迭代器，例如在 for 循环中。
    def __iter__(self):
        return self



"""
因此，迭代器可以迭代，但是可迭代的对象不是迭代器。

除了 __iter__ 方法之外，你可能还想在 Sentence 类中实现
__next__ 方法，让 Sentence 实例既是可迭代的对象，也是自身的
迭代器。可是，这种想法非常糟糕。根据有大量 Python 代码审查经验的
Alex Martelli 所说，这也是常见的反模式。



迭代器模式可用来：
- 访问一个聚合对象的内容而无需暴露它的内部表示
- 支持对聚合对象的多种遍历
- 为遍历不同的聚合结构提供一个统一的接口（即支持多态迭代）
"""