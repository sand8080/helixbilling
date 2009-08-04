from functools import partial
import glob
import sys
import imp
from datetime import datetime

from db.cond import Eq, And
from db.query_builder import select, insert, delete
from db.wrapper import transaction, fetchone_dict

patch_table_name = 'patch'

def get_patches(path):
    names = glob.glob1(path, '[1-9\-]*.py')
    return map(lambda x: x.replace('.py', ''), names)

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

def apply(patches_path, last_applied):
    patches = filter_forward(last_applied, None, get_patches(patches_path))
    dynamic_patch_call(patches_path, patches, 'apply', register_patch)

def revert(patches_path, last_applied):
    patches = filter_backward(None, last_applied, get_patches(patches_path))
    dynamic_patch_call(patches_path, patches, 'revert',  unregister_patch)

def dynamic_patch_call(path, patches, executor_name, registrator):
    sys.path.append(path)
    for p in patches:
        (file, pathname, description) = imp.find_module(p)
        try:
            m = imp.load_module(p, file, pathname, description)
            process_patch(p, pathname, getattr(m, executor_name), registrator)
        finally:
            file.close()

@transaction()
def process_patch(patch_name, patch_path, fun, registrator, curs=None):
    fun(curs)
    if is_table_exist(patch_table_name, curs):
        registrator(patch_name, patch_path, curs)

def register_patch(name, path, curs):
    curs.execute(*insert(patch_table_name, {'name': name, 'path': path, 'date': datetime.now()}))

def unregister_patch(name, path, curs):
    cond = And(Eq('name', name), Eq('path', path))
    curs.execute(*delete(patch_table_name, cond=cond))

def is_table_exist(table_name, curs):
    curs.execute(*select('pg_tables', cond=Eq('tablename', table_name)))
    return len(curs.fetchall()) > 0

@transaction()
def get_last_applied(table_name, curs=None):
    if not is_table_exist(table_name, curs):
        return None
    else:
        curs.execute(*select(table_name, order_by=['-id'], limit=1))
        return fetchone_dict(curs)
