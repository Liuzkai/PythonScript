import random


def random_seed(kwargs):
    node = kwargs['node']
    point_seed = node.parm('npt_seed')
    variant_seed = node.parm('variant_seed')
    pscale_seed = node.parm('pscale_seed')
    angle_seed = node.parm('angle_seed')
    ucx_seed = node.parm('ucx_seed')
    point_seed.set(random.random()*1000)
    variant_seed.set(random.random()*1000)
    pscale_seed.set(random.random()*1000)
    angle_seed.set(random.random()*1000)
    ucx_seed.set(random.random()*1000)
    node.parm('offsetx').set(random.random() * 2000)
    node.parm('offsety').set(random.random() * 2000 + 212.15689)
    node.parm('offsetz').set(random.random() * 2000 - 765.14654)