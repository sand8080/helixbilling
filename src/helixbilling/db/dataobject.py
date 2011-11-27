from helixcore.mapping.objects import Mapped, serialize_field
from helixcore.db.dataobject import Currency, ActionLog #@UnusedImport


class UsedCurrency(Mapped):
    __slots__ = ['id', 'environment_id', 'currencies_ids']
    table = 'used_currency'


class Balance(Mapped):
    __slots__ = ['id', 'environment_id', 'is_active', 'user_id', 'currency_id',
        'real_amount', 'virtual_amount', 'locked_amount', 'overdraft_limit',
    ]
    table = 'balance'


class Transaction(Mapped):
    __slots__ = ['id', 'environment_id', 'user_id', 'balance_id', 'real_amount', 'order_id',
        'virtual_amount', 'creation_date', 'currency_code', 'type', 'serialized_info'
    ]
    table = 'transaction'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'info', 'serialized_info')
        super(Transaction, self).__init__(**d)


class BalanceLock(Mapped):
    __slots__ = ['id', 'environment_id', 'user_id', 'balance_id', 'creation_date', 'order_id',
        'currency_id', 'real_amount', 'virtual_amount', 'locking_order', 'serialized_info']
    table = 'balance_lock'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'info', 'serialized_info')
        super(BalanceLock, self).__init__(**d)
