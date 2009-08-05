from functools import partial

def in_diapasone(begin, end, value):
    return (begin == None or value > begin) and (end == None or value < end)

def version2int(v):
    return map(int, v.split('-'))

def filter_patches(begin, end, patches, reverse=False):
    lst = [p for p in patches if in_diapasone(begin, end, p)]
    lst.sort(key=version2int, reverse=reverse)
    return lst

filter_forward = filter_patches
filter_backward = partial(filter_patches, reverse=True)

