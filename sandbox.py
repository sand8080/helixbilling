
class Balance(object):
    
    __slots__ = ['client_id', 'amount', 'currency']
    
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k in self.__slots__:
                setattr(self, k, v)
            else:
                raise TypeError('Property "%s" undefinded for class Balance' % k)

def f(a, b, c, client_id=None, amount=None, currency=None):
    print a, b, c, client_id, amount, currency

if __name__ == '__main__':
    kw = {'client_id': 1, 'amount': 7.0, 'currency': 'ru'}
    b = Balance(**kw)
#    args = [1, '2', 3]
#    f(*args, **kw)
