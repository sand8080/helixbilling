class Mapped(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            if k in self.__slots__:
                setattr(self, k, kwargs[k])
            else:
                raise TypeError('Property "%s" undefinded' % k)

class Patch(Mapped):
    __slots__ = ['id', 'name', 'path', 'date']
    table = 'patch'
