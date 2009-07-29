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
