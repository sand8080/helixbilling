from cond import quote, quote_list

def __where(cond):
    if cond != None:
        cond_str, params = cond.glue()
        return ('WHERE %s' % cond_str, params)
    else:
        return ('', [])

def __order(order_by):
    if order_by != None:
        orders = []
        for o in order_by:
            if o.startswith('-'):
                orders.append('%s DESC' % quote(o[1:]))
            else:
                orders.append('%s ASC' % quote(o))
        return 'ORDER BY %s' % ','.join(orders)
    else:
        return ''

def select(table, columns=None, cond=None, group_by=None, order_by=None, limit=None, offset=0, for_update=False):
    tpl = {}
    tpl['target']   = '*' if columns == None else quote_list(columns)
    tpl['table']    = quote(table)
    where_str, where_params = __where(cond)
    tpl['where']    = where_str
    tpl['group_by'] = ''  if group_by == None else 'GROUP BY %s' % quote_list(group_by)
    tpl['limit']    = ''  if limit == None else 'LIMIT %d' % limit
    tpl['offset']   = ''  if offset == 0 else 'OFFSET %d' % offset
    tpl['order_by'] = __order(order_by)
    tpl['locking']  = ''  if not for_update else 'FOR UPDATE'

    return (
        ('SELECT %(target)s FROM %(table)s %(where)s %(group_by)s %(order_by)s %(limit)s %(offset)s %(locking)s' % tpl).strip(),
        where_params
    )

def __separate_dict(d):
    d_keys = []
    d_values = []
    for k, v in d.iteritems():
        d_keys.append(k)
        d_values.append(v)
    return d_keys, d_values

def update(table, updates, cond=None):
    tpl = {}
    tpl['table']    = quote(table)
    update_columns, update_params = __separate_dict(updates)
    tpl['updates']  = ','.join(['%s = %%s' % quote(c) for c in update_columns])
    where_str, where_params = __where(cond)
    tpl['where']    = where_str
    return (
        ('UPDATE %(table)s SET %(updates)s %(where)s' % tpl).strip(),
        update_params + where_params
    )

def delete(table, cond=None):
    tpl = {}
    tpl['table']    = quote(table)
    where_str, where_params = __where(cond)
    tpl['where']    = where_str
    return (('DELETE FROM %(table)s %(where)s' % tpl).strip(), where_params)

def insert(table, inserts):
    tpl = {}
    tpl['table']    = quote(table)
    insert_columns, insert_params = __separate_dict(inserts)
    tpl['columns']  = ','.join(map(quote, insert_columns))
    tpl['values']   = ','.join(['%s' for c in insert_columns])
    return (
        ('INSERT INTO %(table)s (%(columns)s) VALUES (%(values)s)' % tpl).strip(),
        insert_params
    )