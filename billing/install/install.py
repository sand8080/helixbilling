from functools import partial
import glob
import sys
import imp
from datetime import datetime

from db.cond import Eq, And
from db.query_builder import select, insert, delete
from db.wrapper import transaction, fetchone_dict

patch_table_name = 'patch'

def filter_diapasone(begin, end, value):
    return (begin == None or value > begin) and (end == None or value < end)

def _sorting_key(v):
    return map(int, v.split('-'))

def filter_patches(begin, end, patches, reverse=False):
    filter_func = partial(filter_diapasone, *(begin,end))
    return sorted(filter(filter_func, patches), key=_sorting_key, reverse=reverse)

filter_forward = filter_patches
filter_backward = partial(filter_patches, **{'reverse': True})

def get_patches(path):
    names = glob.glob1(path, '[1-9\-]*.py')
    return map(lambda x: x.replace('.py', ''), names)

def apply(patches_path, last_applyed):
    patches = filter_forward(last_applyed, None, get_patches(patches_path))
    _dynamic_patch_call(patches_path, patches, 'apply', _register_patch)

def revert(patches_path, last_applyed):
    patches = filter_backward(None, last_applyed, get_patches(patches_path))
    _dynamic_patch_call(patches_path, patches, 'revert',  _unregister_patch)

def _dynamic_patch_call(path, patches, executor_name, registrator):
    sys.path.append(path)
    for p in patches:
        (file, pathname, description) = imp.find_module(p)
        try:
            m = imp.load_module(p, file, pathname, description)
            _process_patch(p, pathname, m.__getattribute__(executor_name), registrator)
        finally:
            file.close()

@transaction()
def _process_patch(patch_name, patch_path, fun, registrator, curs=None):
    fun(curs)
    if is_table_exist(patch_table_name, curs):
        registrator(patch_name, patch_path, curs)

def _register_patch(name, path, curs):
    curs.execute(*insert(patch_table_name, {'name': name, 'path': path, 'date': datetime.now()}))

def _unregister_patch(name, path, curs):
    cond = And(Eq('name', name), Eq('path', path))
    curs.execute(*delete(patch_table_name, cond=cond))

def is_table_exist(table_name, curs):
    curs.execute(*select('pg_tables', cond=Eq('tablename', table_name)))
    return len(curs.fetchall()) > 0

@transaction()
def get_last_applyed(table_name, curs=None):
    if not is_table_exist(table_name, curs):
        return None
    else:
        curs.execute(*select(table_name, order_by=['-id'], limit=1))
        return fetchone_dict(curs)
