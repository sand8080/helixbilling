from helixcore.validol.validol import Optional, AnyOf, NonNegative, Positive, Scheme, Text, IsoDatetime
from helixcore.server.api import ApiCall

amount_validator = (NonNegative(int), NonNegative(int))
nonnegative_amount_validator = (Positive(int), NonNegative(int))
locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

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

GET_CURRENCIES = {}
GET_CURRENCIES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK, currencies=[
        {
            'name': Text(),
            'designation': Text(),
            'cent_factor': Positive(int)
        }
    ]),
    RESPONSE_STATUS_ERROR
)

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

DELETE_BALANCE = {
    'client_id': Text()
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

PRODUCT_STATUS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'product_status': 'unknown',
        }
    ),
    dict(RESPONSE_STATUS_OK,
        **{
            'product_status': 'locked',
            'real_amount': amount_validator,
            'virtual_amount': amount_validator,
            'locked_date': IsoDatetime(),
        }
    ),
    dict(RESPONSE_STATUS_OK,
        **{
            'product_status': 'charged_off',
            'real_amount': amount_validator,
            'virtual_amount': amount_validator,
            'locked_date': IsoDatetime(),
            'chargeoff_date': IsoDatetime(),
        }
    ),
    RESPONSE_STATUS_ERROR
)

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

# --- view operations ---
VIEW_RECEIPTS = {
    'client_id': Text(),
    Optional('start_date'): IsoDatetime(),
    Optional('end_date'): IsoDatetime(),
    'offset': NonNegative(int),
    'limit': Positive(int),
}

VIEW_RECEIPTS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'total': NonNegative(int),
            'receipts': [{
                'client_id': Text(),
                'amount': nonnegative_amount_validator,
                'created_date': IsoDatetime(),
            }],
        }
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_CHARGEOFFS = {
    'client_id': Text(),
    Optional('product_id'): Text(),
    Optional('locked_start_date'): IsoDatetime(),
    Optional('locked_end_date'): IsoDatetime(),
    Optional('chargeoff_start_date'): IsoDatetime(),
    Optional('chargeoff_end_date'): IsoDatetime(),
    'offset': NonNegative(int),
    'limit': Positive(int),
}

VIEW_CHARGEOFFS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'total': NonNegative(int),
            'chargeoffs': [{
                'client_id': Text(),
                'product_id': Text(),
                'real_amount': amount_validator,
                'virtual_amount': amount_validator,
                'locked_date': IsoDatetime(),
                'chargeoff_date': IsoDatetime(),
            }],
        }
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_BALANCE_LOCKS = {
    'client_id': Text(),
    Optional('product_id'): Text(),
    Optional('locked_start_date'): IsoDatetime(),
    Optional('locked_end_date'): IsoDatetime(),
    'offset': NonNegative(int),
    'limit': Positive(int),
}

VIEW_BALANCE_LOCKS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'total': NonNegative(int),
            'balance_locks': [{
                'client_id': Text(),
                'product_id': Text(),
                'real_amount': amount_validator,
                'virtual_amount': amount_validator,
                'locked_date': IsoDatetime(),
            }],
        }
    ),
    RESPONSE_STATUS_ERROR
)

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

    ApiCall('get_currencies_request', Scheme(GET_CURRENCIES)),
    ApiCall('get_currencies_response', Scheme(GET_CURRENCIES_RESPONSE)),

    # balance
    ApiCall('create_balance_request', Scheme(CREATE_BALANCE)),
    ApiCall('create_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_balance_request', Scheme(MODIFY_BALANCE)),
    ApiCall('modify_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_balance_request', Scheme(DELETE_BALANCE)),
    ApiCall('delete_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    # receipt
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
    ApiCall('product_status_response', Scheme(PRODUCT_STATUS_RESPONSE)),

    # list view operations
    ApiCall('view_receipts_request', Scheme(VIEW_RECEIPTS)),
    ApiCall('view_receipts_response', Scheme(VIEW_RECEIPTS_RESPONSE)),

    ApiCall('view_chargeoffs_request', Scheme(VIEW_CHARGEOFFS)),
    ApiCall('view_chargeoffs_response', Scheme(VIEW_CHARGEOFFS_RESPONSE)),

    #TODO: cover me in test_validator
    ApiCall('view_balance_locks_request', Scheme(VIEW_BALANCE_LOCKS)),
    ApiCall('view_balance_locks_response', Scheme(VIEW_BALANCE_LOCKS_RESPONSE)),
]
