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
    __slots__ = [
        'id',
        'client_id', 'product_id',
        'locking_date', 'chargeoff_date',
        'real_amount', 'virtual_amount'
    ]
    table = 'chargeoff'


class MappedAmountView(Mapped):
    __slots__ = [
        'client_id',
        'amount'
    ]


class ReceiptTotalView(MappedAmountView):
    table = 'receipt_total_view'


class BonusTotalView(MappedAmountView):
    table = 'bonus_total_view'


class ChargeoffTotalView(Mapped):
    __slots__ = [
        'client_id',
        'real_amount',
        'virtual_amount'
    ]
    table = 'chargeoff_total_view'


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
