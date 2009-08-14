
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.cond import Eq, And
from helixcore.mapping.actions import get

from helixbilling.domain.objects import Currency, Balance, BalanceLock, ChargeOff
from helixbilling.logic.exceptions import  DataIntegrityError, ActionNotAllowedError, ApplicationError

def get_currency_by_name(curs, name, for_update=False):
    try:
        return get(curs, Currency, Eq('name', name), for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('Currency with name %s not found in system' % name)

def get_currency_by_balance(curs, balance, for_update=False):
    try:
        return get(curs, Currency, Eq('id', balance.currency_id), for_update)
    except EmptyResultSetError:
        raise ApplicationError('Currency with id %s (related to balance of client ID %d) not found in system' %
            (balance.currency_id, balance.client_id))

def get_balance(curs, client_id, active_only=True, for_update=False):
    try:
        balance = get(curs, Balance, Eq('client_id', client_id), for_update)
        if active_only and balance.active == 0:
            raise ActionNotAllowedError('Balance related to client ID %d is not active' % client_id)
        return balance
    except EmptyResultSetError:
        raise DataIntegrityError('Balance related to client ID %d not found in system' % client_id)

def try_get_lock(curs, client_id, product_id, for_update=False):
    '''
    @return: BalanceLock on success, raises EmptyResultSetError if no such lock
    '''
    return get(curs, BalanceLock, And(Eq('client_id', client_id), Eq('product_id', product_id)), for_update)

def try_get_chargeoff(curs, client_id, product_id, for_update=False):
    '''
    @return: ChargeOff on success, raises EmptyResultSetError if no such charge-off
    '''
    return get(curs, ChargeOff, And(Eq('client_id', client_id), Eq('product_id', product_id)), for_update)

def compose_amount(currency, amount_spec, int_part, cent_part):
    '''
    (500, 50) -> 50050 if cent_factor is 100
    '''
    if int_part < 0:
        raise DataIntegrityError('Integer part of %s amount is negative' % amount_spec)
    if cent_part < 0:
        raise DataIntegrityError('Cent part of %s amount is negative' % amount_spec)

    return currency.cent_factor * int_part + cent_part

def decompose_amount(currency, cent_amount):
    '''
    50050 -> (500, 50) if cent_factor is 100
    '''
    return (cent_amount / currency.cent_factor, cent_amount % currency.cent_factor)
