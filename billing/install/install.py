from functools import partial
import glob

def filter_diapasone(begin, end, value):
    return (begin == None or value > begin) and (end == None or value < end)

def sorting_key(v):
    return map(int, v.split('-'))

def filter_patches(begin, end, patches, reverse=False):
    filter_func = partial(filter_diapasone, *(begin,end))
    return sorted(filter(filter_func, patches), key=sorting_key, reverse=reverse)

filter_forward = filter_patches
filter_backward = partial(filter_patches, **{'reverse': True})

def get_patches(path):
    names = glob.glob1(path, '[1-9\-]*.py')
    return map(lambda x: x.replace('.py', ''), names)