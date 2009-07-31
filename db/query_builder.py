from cond import quote, quote_list, quote_value

def __where(cond):
    return '' if cond is None else 'WHERE %s' % cond

def select(table, columns=None, cond=None, group_by=None, order_by=None, limit=None, offset=0, for_update=False):
    tpl = {}
    tpl['target']   = '*' if columns == None else quote_list(columns)
    tpl['table']    = quote(table)
    tpl['where']    = __where(cond)
    tpl['group_by'] = ''  if group_by == None else 'GROUP BY %s' % quote_list(group_by)
    tpl['limit']    = ''  if limit == None else 'LIMIT %d' % limit
    tpl['offset']   = ''  if offset == 0 else 'OFFSET %d' % offset
    tpl['order_by'] = ''
    tpl['locking']  = ''  if not for_update else 'FOR UPDATE'

    if order_by != None:
        if order_by[0] == '-':
            tpl['order_by'] = 'ORDER BY %s DESC' % quote_list(order_by[1:])
        else:
            tpl['order_by'] = 'ORDER BY %s ASC' % quote_list(order_by)

    return (
        'SELECT %(target)s FROM %(table)s %(where)s %(group_by)s %(order_by)s %(limit)s %(offset)s %(locking)s' % tpl
    ).strip()

def update(table, updates, cond):
    tpl = {}
    tpl['table']    = quote(table)
    tpl['where']    = __where(cond)
    tpl['updates']  = ','.join(['%s = %s' % (quote(k), quote_value(v)) for (k, v) in updates.iteritems()])
    return ('UPDATE %(table)s SET %(updates)s %(where)s' % tpl).strip()

def delete(table, cond):
    tpl = {}
    tpl['table']    = quote(table)
    tpl['where']    = __where(cond)
    return ('DELETE FROM %(table)s %(where)s' % tpl).strip()

def insert(table, inserts):
    tpl = {}
    tpl['table']    = quote(table)
    columns = inserts.keys()
    tpl['columns']  = ','.join(map(quote, columns))
    tpl['values']   = ','.join(map(lambda k: '%s' % quote_value(inserts[k]), columns))
    return ('INSERT INTO %(table)s (%(columns)s) VALUES (%(values)s)' % tpl).strip()