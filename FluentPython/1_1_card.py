import collections

# 构建一个简单的类来表示一张纸牌。namedtuple用于构建只有少数属性但是没有方法的对象，比如数据库条目。
Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suit = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suit for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, item):
        return self._cards[item]


# 如何使用namedtuple:
beer_card = Card('7', 'diamonds')
print(beer_card)  # 返回： Card(rank='7', suit='diamonds')

# 因为定义了__len__内置函数，则拥有的数组的一些方法
deck = FrenchDeck()
print(len(deck))  # return: 52
print(deck[7])  # return: Card(rank='9', suit='spades')

# 随机抽一张牌
from random import choice

print(choice(deck))  # Card(rank='8', suit='clubs')  结果是随机的
print(choice(deck))  # Card(rank='3', suit='diamonds')  结果是随机的

# 特殊方法的好处很多，我们只要定义了其中一类特殊函数(例如 __getitem__)，和其相关的特性就都有了：
print(deck[34:37])  # [Card(rank='10', suit='clubs'), Card(rank='J', suit='clubs'), Card(rank='Q', suit='clubs')]
print(Card('34', 'apple') in deck)  # False

# 能否实现排序了呢？
suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)
def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


for card in sorted(deck, key=spades_high):
    print(card)

# 我们通过实现__len__和__getitem__这两个特殊方法，FrenchDeck就跟一个python自有的序列数据类型一样，可以体现出Python的核心语言特性（例如
# 迭代和切片)，但是目前还不能实现洗牌功能，但是只要简单的实现__setitem__方法即可实现。

# 特殊方法是为了给解释器调用的，我们并不会显示调用他们。
