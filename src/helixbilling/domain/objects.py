from helixcore.mapping.objects import Mapped


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
        'locked_date', 'amount'
    ]
    table = 'balance_lock'


class ChargeOff(Mapped):
    __slots__ = [
        'id',
        'client_id', 'product_id',
        'locked_date', 'chargeoff_date',
        'amount'
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


class ChargeoffTotalView(MappedAmountView):
    table = 'chargeoff_total_view'
