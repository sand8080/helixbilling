import re

from helixcore.validol.validol import Optional, AnyOf, NonNegative, Positive, Scheme, Text
from helixcore.server.api import ApiCall

amount_validator = (NonNegative(int), NonNegative(int))
nonnegative_amount_validator = (Positive(int), NonNegative(int))
locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

iso_datetime_validator = re.compile(r"""
    (\d{2,4})
    (?:-?([01]\d))?
    (?:-?([0-3]\d))?
    (?:T
        ([0-2]\d)
        (?::?([0-5]\d))?
        (?::?([0-5]\d))?
        (?:[\,\.](\d+))?
    )?
    (Z|
        ([+-][0-2]\d)
        (?::?([0-5]\d))?
    )?
    """
)

PING = {
}

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'category': Text(),
    'message': Text(),
}

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

# --- currency ---
ADD_CURRENCY = {
    'name': Text(),
    'designation': Text(),
    Optional('cent_factor'): Positive(int),
}

MODIFY_CURRENCY = {
    'name': Text(),
    Optional('designation'): Text(),
    Optional('cent_factor'): Positive(int),
}

DELETE_CURRENCY = {
    'name': Text(),
}

# --- balance ---
CREATE_BALANCE = {
    'client_id': Text(),
    'active': AnyOf(0, 1),
    'currency_name': Text(),
    'overdraft_limit': amount_validator,
    Optional('locking_order'): locking_order_validator
}

MODIFY_BALANCE = {
    'client_id': Text(),
    Optional('active'): AnyOf(0, 1),
    Optional('overdraft_limit'): amount_validator,
    Optional('locking_order'): locking_order_validator
}

# --- operations ---
ENROLL_RECEIPT = {
    'client_id': Text(),
    'amount': nonnegative_amount_validator,
}

LOCK = {
    'client_id': Text(),
    'product_id': Text(),
    'amount': nonnegative_amount_validator,
}

LOCK_LIST = {
    'locks': [LOCK]
}

UNLOCK = {
    'client_id': Text(),
    'product_id': Text(),
}

UNLOCK_LIST = {
    'unlocks': [UNLOCK]
}

PRODUCT_STATUS = {
    'client_id': Text(),
    'product_id': Text(),
}

ENROLL_BONUS = {
    'client_id': Text(),
    'amount': nonnegative_amount_validator,
}

CHARGEOFF = {
    'client_id': Text(),
    'product_id': Text(),
}

CHARGEOFF_LIST = {
    'chargeoffs': [CHARGEOFF]
}

# --- list operations ---
LIST_RECEIPTS = {
    'client_id': Text(),
    Optional('start_date'): iso_datetime_validator,
    Optional('end_date'): iso_datetime_validator,
    'offset': NonNegative(int),
    'limit': Positive(int),
}

LIST_CHARGEOFFS = {
    'client_id': Text(),
    Optional('product_id'): Text(),
    Optional('locked_start_date'): iso_datetime_validator,
    Optional('locked_end_date'): iso_datetime_validator,
    Optional('chargeoff_start_date'): iso_datetime_validator,
    Optional('chargeoff_end_date'): iso_datetime_validator,
    'offset': NonNegative(int),
    'limit': Positive(int),
}

LIST_BALANCE_LOCK = {
    'client_id': Text(),
    Optional('product_id'): Text(),
    Optional('locked_start_date'): iso_datetime_validator,
    Optional('locked_end_date'): iso_datetime_validator,
    'offset': NonNegative(int),
    'limit': Positive(int),
}

api_scheme = [
    ApiCall('ping_request', Scheme(PING)),
    ApiCall('ping_response', Scheme(RESPONSE_STATUS_ONLY)),

    # currency
    ApiCall('add_currency_request', Scheme(ADD_CURRENCY)),
    ApiCall('add_currency_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_currency_request', Scheme(MODIFY_CURRENCY)),
    ApiCall('modify_currency_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_currency_request', Scheme(DELETE_CURRENCY)),
    ApiCall('delete_currency_response', Scheme(RESPONSE_STATUS_ONLY)),

    # balance
    ApiCall('create_balance_request', Scheme(CREATE_BALANCE)),
    ApiCall('create_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_balance_request', Scheme(MODIFY_BALANCE)),
    ApiCall('modify_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    # recipt
    ApiCall('enroll_receipt_request', Scheme(ENROLL_RECEIPT)),
    ApiCall('enroll_receipt_response', Scheme(RESPONSE_STATUS_ONLY)),

    # bonus
    ApiCall('enroll_bonus_request', Scheme(ENROLL_BONUS)),
    ApiCall('enroll_bonus_response', Scheme(RESPONSE_STATUS_ONLY)),

    # lock
    ApiCall('lock_request', Scheme(LOCK)),
    ApiCall('lock_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('lock_list_request', Scheme(LOCK_LIST)),
    ApiCall('lock_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    # unlock
    ApiCall('unlock_request', Scheme(UNLOCK)),
    ApiCall('unlock_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('unlock_list_request', Scheme(UNLOCK_LIST)),
    ApiCall('unlock_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    # chargeoff
    ApiCall('chargeoff_request', Scheme(CHARGEOFF)),
    ApiCall('chargeoff_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('chargeoff_list_request', Scheme(CHARGEOFF_LIST)),
    ApiCall('chargeoff_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    # product
    ApiCall('product_status_request', Scheme(PRODUCT_STATUS)),
    ApiCall('product_status_response', Scheme(RESPONSE_STATUS_ONLY)),

    # list view operations
    ApiCall('list_receipts_request', Scheme(LIST_RECEIPTS)),
    ApiCall('list_receipts_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('list_chargeoffs_request', Scheme(LIST_CHARGEOFFS)),
    ApiCall('list_chargeoffs_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('list_balance_locks_request', Scheme(LIST_BALANCE_LOCK)),
    ApiCall('list_balance_locks_response', Scheme(RESPONSE_STATUS_ONLY)),
]
