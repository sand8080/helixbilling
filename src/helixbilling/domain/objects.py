from helixcore.mapping.objects import Mapped


class BillingManager(Mapped):
    __slots__ = ['id', 'login', 'password']
    table = 'billing_manager'


class ActionLog(Mapped):
    __slots__ = [
        'id',
        'client_ids', 'action',
        'request_date',
        'request', 'response',
    ]
    table = 'action_log'


class Currency(Mapped):
    __slots__ = ['id', 'name', 'designation', 'cent_factor']
    table = 'currency'


class Balance(Mapped):
    __slots__ = [
        'id', 'active',
        'client_id', 'currency_id',
        'created_date',
        'available_real_amount',
        'available_virtual_amount',
        'overdraft_limit',
        'locking_order',
        'locked_amount',
    ]
    table = 'balance'


class Receipt(Mapped):
    __slots__ = [
        'id',
        'client_id',
        'created_date',
        'amount'
    ]
    table = 'receipt'


class Bonus(Mapped):
    __slots__ = [
        'id',
        'client_id',
        'created_date', 'amount'
    ]
    table = 'bonus'


class BalanceLock(Mapped):
    __slots__ = [
        'id',
        'client_id', 'product_id',
        'locked_date',
        'real_amount', 'virtual_amount'
    ]
    table = 'balance_lock'


class ChargeOff(Mapped):
    __slots__ = [
        'id',
        'client_id', 'product_id',
        'locked_date', 'chargeoff_date',
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
