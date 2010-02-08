from helixcore.mapping.objects import Mapped


class Operator(Mapped):
    __slots__ = ['id', 'login', 'password']
    table = 'operator'

    def __repr__(self, except_attrs=()):
        return super(Operator, self).__repr__(except_attrs=except_attrs + ('password',))


class Currency(Mapped):
    __slots__ = ['id', 'code', 'cent_factor', 'name', 'location']
    table = 'currency'


class Balance(Mapped):
    __slots__ = ['id', 'operator_id', 'active', 'customer_id', 'currency_id', 'creation_date',
        'available_real_amount', 'available_virtual_amount', 'locking_order', 'locked_amount',
        'overdraft_limit',
    ]
    table = 'balance'


class Receipt(Mapped):
    __slots__ = ['id', 'operator_id', 'customer_id', 'creation_date', 'amount']
    table = 'receipt'


class Bonus(Mapped):
    __slots__ = ['id', 'operator_id',  'customer_id', 'creation_date', 'amount']
    table = 'bonus'


class BalanceLock(Mapped):
    __slots__ = ['id', 'operator_id',  'customer_id', 'order_id', 'order_type', 'locking_date',
        'real_amount', 'virtual_amount']
    table = 'balance_lock'


class ChargeOff(Mapped):
    __slots__ = ['id', 'operator_id',  'customer_id', 'order_id', 'order_type',
        'real_amount', 'virtual_amount', 'chargeoff_date']
    table = 'chargeoff'


class ActionLog(Mapped):
    __slots__ = [
        'id',
        'operator_id',
        'custom_operator_info'
        'customer_ids', 'action',
        'request_date',
        'request', 'response',
    ]
    table = 'action_log'
