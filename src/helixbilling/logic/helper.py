from helixcore.server.exceptions import  DataIntegrityError, ActionNotAllowedError


def compose_amount(currency, int_part, cent_part):
    '''
    (500, 50) -> 50050 if cent_factor is 100
    '''
    if int_part < 0:
        raise DataIntegrityError('Integer part of amount is negative')
    if cent_part < 0:
        raise DataIntegrityError('Cent part of amount is negative')
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
    return '%s %s' % ('.'.join(map(str, decompose_amount(currency, composed_amount))), currency.name)

