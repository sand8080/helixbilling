import iso8601 #@UnresolvedImport

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.sql import Eq, And, NullLeaf, MoreEq, Less
from helixcore.mapping.actions import get
from helixcore.server.exceptions import  DataIntegrityError, ActionNotAllowedError, ApplicationError

from helixbilling.domain.objects import Currency, Balance, BalanceLock, ChargeOff

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
            raise ActionNotAllowedError('Balance related to client ID %s is not active' % client_id)
        return balance
    except EmptyResultSetError:
        raise DataIntegrityError('Balance related to client ID %s not found in system' % client_id)

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

def get_date_filters(date_filters, data):
    '''
    adds date filtering parameters from data to cond.
    @param date_filters: is tuple of
        (start_date_filter_name, end_date_filter_name, db_filtering_field_name)
    @param data: dict of request data
    @return: db filtering condition
    '''
    cond = NullLeaf()
    for start_date, end_date, db_field in date_filters:
        if start_date in data:
            cond = And(cond, MoreEq(db_field, iso8601.parse_date(data[start_date])))
        if end_date in data:
            cond = And(cond, Less(db_field, iso8601.parse_date(data[end_date])))
    return cond

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

def get_available_resources(balance):
    return {
        'available_real_amount': balance.available_real_amount + balance.overdraft_limit,
        'available_virtual_amount': balance.available_virtual_amount
    }

def compute_locks(currency, balance, lock_amount):
    """
    Returns {field_name: locked_amount}. field_names are from locking_order.
    If locking_order is None, then default locking order used: [available_real_amount, available_real_amount].

    If balance has overdraft_limit > 0 and available_real_amount is in locking_order or locking_order is None,
    then we can decrease available_real_amount until reach -overdraft_limit value.

    ActionNotAllowedError exception raises if money not enough.
    """
    if balance.locking_order is None:
        locking_order = ['available_real_amount', 'available_virtual_amount']
    else:
        locking_order = balance.locking_order

    available_resources = get_available_resources(balance)
    amount_to_lock = lock_amount
    locked_resources = dict(zip(locking_order, [0 for _i in locking_order]))
    for resource_name in locking_order:
        if amount_to_lock <= 0:
            break
        available_to_lock = min(amount_to_lock, available_resources[resource_name])
        locked_resources[resource_name] += available_to_lock

        amount_to_lock -= available_to_lock
        available_resources[resource_name] -= available_to_lock

    if amount_to_lock > 0:
        lockable_descr = []
        available_resources = get_available_resources(balance)
        for resource_name in locking_order:
            lockable_descr.append('%s %s' % (resource_name,
                human_readable_amount(currency, available_resources[resource_name]))
            )
        error = {
            'lock_amount': human_readable_amount(currency, lock_amount),
            'client_id': balance.client_id,
            'lockable_descr': ', '.join(lockable_descr)
        }
        raise ActionNotAllowedError(
            'Can not lock %(lock_amount)s on balance of client %(client_id)s.'
            'Available to lock: %(lockable_descr)s' % error
        )
    return locked_resources

def human_readable_amount(currency, composed_amount):
    return '%s %s' % ('.'.join(map(str, decompose_amount(currency, composed_amount))), currency.designation)

