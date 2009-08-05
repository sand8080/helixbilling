class Mapped(object):
    __slots__ = []

    def __init__(self, **kwargs):
        for k in kwargs:
            if k in self.__slots__:
                setattr(self, k, kwargs[k])
            else:
                raise TypeError('Property "%s" undefinded' % k)
    
    def update(self, data):
        self.__dict__.update(data)
    
#class Patch(Mapped):
#    __slots__ = ['id', 'name', 'path', 'date']
#    table = 'patch'
