from math import log10
from decimal import Decimal

from helixcore.error import ActionNotAllowedError
from helixcore.utils import filter_dict
from helixbilling.error import MoneyNotEnough


def decimal_to_cents(currency, dec):
    int_part = int(dec)
    prec = int(round(log10(currency.cent_factor)))
    cent_part = int((dec - int_part) * 10 ** prec)
    return currency.cent_factor * int_part + cent_part


def cents_to_decimal(currency, cents):
    prec = int(round(log10(currency.cent_factor)))
    if cents < 0:
        cents = -1 * cents
        format = '-%%d.%%0%dd' % prec
    else:
        format = '%%d.%%0%dd' % prec
    int_part = cents / currency.cent_factor
    cent_part =  cents % currency.cent_factor
    return Decimal(format % (int_part, cent_part))


def decimal_texts_to_cents(data, currency, amount_fields):
    result = dict(data)
    amount_data = filter_dict(amount_fields, data)
    for k, v in amount_data.items():
        amount_data[k] = decimal_to_cents(currency, Decimal(v))
    result.update(amount_data)
    return result


def get_lockable_amounts(balance):
    return {
        'real_amount': balance.real_amount + balance.overdraft_limit,
        'virtual_amount': balance.virtual_amount
    }


def compute_locks(balance, lock_amount, locking_order):
    """
    Returns {field_name: locked_amount}. field_names are from locking_order.

    If balance has overdraft_limit > 0 and real_amount is in locking_order or locking_order is None,
    then we can decrease real_amount until reach -overdraft_limit value.

    ActionNotAllowedError exception raises if money not enough.
    """
    amounts_to_lock = dict([(a, 0) for a in locking_order])
    lockable_amounts = get_lockable_amounts(balance)

    remain_to_lock = lock_amount
    for amount_name in locking_order:
        if remain_to_lock <= 0:
            break
        available_to_lock = min(remain_to_lock, lockable_amounts[amount_name])
        amounts_to_lock[amount_name] += available_to_lock

        remain_to_lock -= available_to_lock
        lockable_amounts[amount_name] -= available_to_lock

    if remain_to_lock > 0:
        raise MoneyNotEnough()
    return amounts_to_lock
