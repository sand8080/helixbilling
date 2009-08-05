
from helixcore.mapping.objects import Mapped

class Currency(Mapped):
    __slots__ = ['id', 'name', 'designation', 'cent_factor']
    table = 'currency'

