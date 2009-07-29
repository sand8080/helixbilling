def quote(val):
    q, s = '"', '.'
    return  s.join([x.startswith(q) and x.endswith(q) and x or '"%s"' % x for x in val.split(s)])

def quote_list(lst, separator=','):
    return separator.join(map(quote, lst))

def quote_value(val, quote="'"):
    if isinstance(val, str) and not (val.startswith(quote) and val.endswith(quote)):
        return "'%s'" % val
    else:
        return val

def _triple_expr(lh, oper, rh):
    return '%s %s %s' % (lh, oper, rh)

class Cond(object):
    def __init__(self, lh, oper, rh):
        self.lh = lh
        self.oper = oper
        self.rh = rh
    def glue(self):
        return _triple_expr(
            quote(self.lh),
            self.oper,
            quote_value(self.rh)
        )

class EqCond(Cond):
    def __init__(self, lh, rh):
        super(EqCond, self).__init__(lh, '=', rh)

class NotCond(object):
    def __init__(self, lh, rh):
        self.lh = lh
        self.rh = rh
    def glue(self):
        return _triple_expr(quote(self.lh), 'NOT', self.rh)
    
class ScopedCond(object):
    def __init__(self, cond):
        self.cond = cond
    def glue(self):
        return '(%s)' % self.cond.glue()

class AndCond(object):
    def __init__(self, lh, rh):
        self.lh = lh
        self.rh = rh
    def glue(self):
        return _triple_expr(self.lh.glue(), 'AND', self.rh.glue())

class OrCond(object):
    def __init__(self, lh, rh):
        self.lh = lh
        self.rh = rh
    def glue(self):
        return _triple_expr(self.lh.glue(), 'OR', self.rh.glue())

def select(table, columns=None, cond=None, group_by=None, order_by=None, limit=0, offset=0, for_update=False):
    tpl = {}
    tpl['target']   = '*' if columns == None else quote_list(columns)
    tpl['table']    = quote(table)
    tpl['where']    = ''  if cond is None else 'WHERE %s' % cond.glue()
    tpl['group_by'] = ''  if group_by == None else 'GROUP BY %s' % quote_list(group_by)
    tpl['limit']    = ''  if limit == 0 else 'LIMIT %d' % limit
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

#    if columns:
#        parts.append(", ".join( escape(column) for column in columns ))
#    else:
#        parts.append("*")
#    parts.append("FROM")
#    parts.append(select_from)
#
#    if join:
#        join_sql, join_params = join
#        parts.append(join_sql)
#        params.extend(join_params)
#    if conditions:
#        where_query, where_params = where(**conditions)
#        parts.append(where_query)
#        params += where_params
#    if group_by:
#        group_parts = []
#        parts.append("GROUP BY")
#        for col in group_by:
#            group_parts.append(escape(col))
#        parts.append(", ".join(group_parts))
#    if order_by:
#        order_parts = []
#        parts.append("ORDER BY")
#        for col in order_by:
#            if col[0] == "-":
#                order_parts.append(escape(col[1:]) + " DESC")
#            else:
#                order_parts.append(escape(col) + " ASC")
#        parts.append(", ".join(order_parts))
#    if limit:
#        parts.append("LIMIT %d" % limit)
#    if offset:
#        parts.append("OFFSET %d" % offset)
#    query = " ".join(parts) + ";"
#    return (query, params)
