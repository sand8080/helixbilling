from helixcore.mapping.objects import Mapped



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
        'real_amount', 'virtual_amount', 'locking_date', 'chargeoff_date']
    table = 'chargeoff'


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_user_info', 'actor_user_id',
        'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'
