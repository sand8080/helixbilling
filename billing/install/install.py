from functools import partial
import glob
import sys
import imp

from db.cond import Eq
from db.query_builder import select
from db.wrapper import transaction

patch_table_name = 'patch'

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

def apply(path, last_applyed):
    patches = filter_forward(last_applyed, None, get_patches(path))
    sys.path.append(path)
    for p in patches:
        (file, pathname, description) = imp.find_module(p)
        try:
            m = imp.load_module(p, file, pathname, description)
            fun = m.__getattribute__('apply')
            fun()
        finally:
            file.close()

def apply(patches_path, last_applyed):
    patches = filter_forward(last_applyed, None, get_patches(patches_path))
    dynamic_patch_call(patches_path, patches, 'apply')

def revert(patches_path, last_applyed):
    patches = filter_backward(None, last_applyed, get_patches(patches_path))
    dynamic_patch_call(patches_path, patches, 'revert')

def dynamic_patch_call(path, patches, f_name):
    sys.path.append(path)
    for p in patches:
        (file, pathname, description) = imp.find_module(p)
        try:
            m = imp.load_module(p, file, pathname, description)
            fun = m.__getattribute__(f_name)
            register_patch(p, pathname)
            fun()
        finally:
            file.close()

@transaction()
def register_patch(patch_name, patch_path, curs=None):
    if is_table_exist(patch_table_name, curs):
        pass
    else:
        pass

def is_table_exist(table_name, curs):
    curs.execute(*select('pg_tables', cond=Eq('tablename', table_name)))
    return len(curs.fetchall()) > 0

def get_last_applyed(table_name, curs):
    if not is_table_exist(table_name, curs):
        return None
    else:
        return select(order_by=['-id'], limit=1)
