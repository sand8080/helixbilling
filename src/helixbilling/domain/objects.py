
from helixcore.mapping.objects import Mapped

class Currency(Mapped):
    __slots__ = ['id', 'name', 'designation', 'cent_factor']
    table = 'currency'

class Balance(Mapped):
    __slots__ = [
        'id', 'active',
        'client_id', 'currency_id', 
        'created_date',
        'available_amount', 'locked_amount', 'overdraft_limit'
    ]
    table = 'balance'

class Receipt(Mapped):
    __slots__ = [
        'id',
        'client_id', 
        'created_date', 'amount'
    ]
    table = 'receipt'

class BalanceLock(Mapped):
    __slots__ = [
        'id',
        'client_id', 'product_id', 
        'locked_date', 'amount'
    ]
    table = 'balance_lock'
