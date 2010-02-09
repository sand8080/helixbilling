from helixcore.server.api import ApiCall
from helixcore.validol.validol import (Optional, AnyOf, NonNegative, Positive, Scheme,
    Text, IsoDatetime, DecimalText, FlatDict)

NullableText = AnyOf(Text(), None)

locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

PING = {}

RESPONSE_STATUS_OK = {'status': 'ok'}

PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'category': Text(),
    'message': Text(),
    'details': [FlatDict()],
}

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

AUTH_INFO = {
    'login': Text(),
    'password': Text(),
    Optional('custom_operator_info'): NullableText,
}

# --- currencies ---
VIEW_CURRENCIES = {Optional('custom_operator_info'): NullableText,}

VIEW_CURRENCIES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK, currencies=[
        {
            'code': Text(),
            'cent_factor': Positive(int),
            'name': Text(),
            'location': Text(),
        }
    ]),
    RESPONSE_STATUS_ERROR
)


# --- operator ---
ADD_OPERATOR = AUTH_INFO

MODIFY_OPERATOR = dict(
    {
        Optional('new_login'): Text(),
        Optional('new_password'): Text(),
    },
    **AUTH_INFO
)


# --- balance ---
ADD_BALANCE = dict(
    {
        'customer_id': Text(),
        'active': bool,
        'currency': Text(),
        Optional('overdraft_limit'): DecimalText(),
        Optional('locking_order'): locking_order_validator
    },
    **AUTH_INFO
)

MODIFY_BALANCE = dict(
    {
        'customer_id': Text(),
        Optional('new_active'): bool,
        Optional('new_overdraft_limit'): DecimalText(),
        Optional('new_locking_order'): locking_order_validator
    },
    **AUTH_INFO
)

DELETE_BALANCE = dict(
    {'customer_id': Text()},
    **AUTH_INFO
)

GET_BALANCE = dict(
    {'customer_id': Text()},
    **AUTH_INFO
)

BALANCE_INFO = {
    'customer_id': Text(),
    'active': bool,
    'currency_code': Text(),
    'creation_date': IsoDatetime(),
    'available_real_amount': DecimalText(),
    'available_virtual_amount': DecimalText(),
    'overdraft_limit': DecimalText(),
    'locked_amount': DecimalText(),
    'locking_order': locking_order_validator,
}

GET_BALANCE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **BALANCE_INFO
    ),
    RESPONSE_STATUS_ERROR
)


VIEW_BALANCES = dict(
    {
        'filter_params': {
            Optional('customer_ids'): [Text()],
        },
        'paging_params': PAGING_PARAMS,
    },
    **AUTH_INFO
)

VIEW_BALANCES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'balances': [BALANCE_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)


# --- common income money structures ---
ENROLL_INCOME = dict(
    {
        'customer_id': Text(),
        'amount': DecimalText(),
    },
    **AUTH_INFO
)

VIEW_INCOMES = dict(
    {
        'filter_params': {
            Optional('customer_ids'): [Text()],
            Optional('from_creation_date'): IsoDatetime(),
            Optional('to_creation_date'): IsoDatetime(),
        },
        'paging_params': PAGING_PARAMS,
    },
    **AUTH_INFO
)

INCOME_INFO = {
    'customer_id': Text(),
    'amount': DecimalText(),
    'currency': Text(),
    'creation_date': IsoDatetime(),
}

# --- receipt ---
ENROLL_RECEIPT = ENROLL_INCOME

VIEW_RECEIPTS = VIEW_INCOMES

VIEW_RECEIPTS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'receipts': [INCOME_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)


# ---  bonus ---
ENROLL_BONUS = ENROLL_INCOME

VIEW_BONUSES = VIEW_INCOMES

VIEW_BONUSES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'bonuses': [INCOME_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)


# --- lock ---
BALANCE_LOCK_DATA = {
    'customer_id': Text(),
    'order_id': Text(),
    Optional('order_type'): Text(),
    'amount': DecimalText(),
}

BALANCE_LOCK = dict(BALANCE_LOCK_DATA, **AUTH_INFO)

BALANCE_LOCK_LIST = dict(
    {'locks': [BALANCE_LOCK_DATA]},
    **AUTH_INFO
)

VIEW_BALANCE_LOCKS = dict(
    {
        'filter_params': {
            Optional('customer_ids'): [Text()],
            Optional('order_id'): Text(),
            Optional('order_type'): NullableText,
            Optional('from_locking_date'): IsoDatetime(),
            Optional('to_locking_date'): IsoDatetime(),
        },
        'paging_params': PAGING_PARAMS,
    },
    **AUTH_INFO
)

VIEW_BALANCE_LOCKS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'balance_locks': [{
                'customer_id': Text(),
                'order_id': Text(),
                'order_type': NullableText,
                'real_amount': DecimalText(),
                'virtual_amount': DecimalText(),
                'currency': Text(),
                'locking_date': IsoDatetime(),
            }],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

# --- unlock ---
#
BALANCE_UNLOCK_DATA = {
    'customer_id': Text(),
    'order_id': Text(),
}

BALANCE_UNLOCK = dict(BALANCE_UNLOCK_DATA, **AUTH_INFO)

BALANCE_UNLOCK_LIST = dict(
    {'unlocks': [BALANCE_UNLOCK_DATA]},
    **AUTH_INFO
)


# --- chargeoff ---
CHARGEOFF_DATA = {
    'customer_id': Text(),
    'order_id': Text(),
}

CHARGEOFF = dict(CHARGEOFF_DATA, **AUTH_INFO)

CHARGEOFF_LIST = dict(
    {'chargeoffs': [CHARGEOFF_DATA]},
    **AUTH_INFO
)

VIEW_CHARGEOFFS = dict(
    {
        'filter_params': {
            Optional('customer_ids'): [Text()],
            Optional('order_id'): Text(),
            Optional('order_type'): NullableText,
            Optional('from_chargeoff_date'): IsoDatetime(),
            Optional('to_chargeoff_date'): IsoDatetime(),
        },
        'paging_params': PAGING_PARAMS,
    },
    **AUTH_INFO
)

VIEW_CHARGEOFFS_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'chargeoffs': [{
                'customer_id': Text(),
                'order_id': Text(),
                'order_type': NullableText,
                'real_amount': DecimalText(),
                'virtual_amount': DecimalText(),
                'currency': Text(),
                'chargeoff_date': IsoDatetime(),
            }],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

#PRODUCT_STATUS = dict(
#    {
#        'client_id': Text(),
#        'product_id': Text(),
#    },
#    **AUTH_INFO
#)
#
#PRODUCT_STATUS_RESPONSE = AnyOf(
#    dict(RESPONSE_STATUS_OK,
#        **{
#            'product_status': 'unknown',
#        }
#    ),
#    dict(RESPONSE_STATUS_OK,
#        **{
#            'product_status': 'locked',
#            'real_amount': amount_validator,
#            'virtual_amount': amount_validator,
#            'locked_date': IsoDatetime(),
#        }
#    ),
#    dict(RESPONSE_STATUS_OK,
#        **{
#            'product_status': 'charged_off',
#            'real_amount': amount_validator,
#            'virtual_amount': amount_validator,
#            'locked_date': IsoDatetime(),
#            'chargeoff_date': IsoDatetime(),
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#

protocol = [
    ApiCall('ping_request', Scheme(PING)),
    ApiCall('ping_response', Scheme(RESPONSE_STATUS_ONLY)),

    # currencies
    ApiCall('view_currencies_request', Scheme(VIEW_CURRENCIES)),
    ApiCall('view_currencies_response', Scheme(VIEW_CURRENCIES_RESPONSE)),

    # operator
    ApiCall('add_operator_request', Scheme(ADD_OPERATOR)),
    ApiCall('add_operator_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_operator_request', Scheme(MODIFY_OPERATOR)),
    ApiCall('modify_operator_response', Scheme(RESPONSE_STATUS_ONLY)),

    # balance
    ApiCall('add_balance_request', Scheme(ADD_BALANCE)),
    ApiCall('add_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_balance_request', Scheme(MODIFY_BALANCE)),
    ApiCall('modify_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_balance_request', Scheme(DELETE_BALANCE)),
    ApiCall('delete_balance_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('get_balance_request', Scheme(GET_BALANCE)),
    ApiCall('get_balance_response', Scheme(GET_BALANCE_RESPONSE)),

    ApiCall('view_balances_request', Scheme(VIEW_BALANCES)),
    ApiCall('view_balances_response', Scheme(VIEW_BALANCES_RESPONSE)),

    # receipt
    ApiCall('enroll_receipt_request', Scheme(ENROLL_RECEIPT)),
    ApiCall('enroll_receipt_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('view_receipts_request', Scheme(VIEW_RECEIPTS)),
    ApiCall('view_receipts_response', Scheme(VIEW_RECEIPTS_RESPONSE)),

    # bonus
    ApiCall('enroll_bonus_request', Scheme(ENROLL_BONUS)),
    ApiCall('enroll_bonus_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('view_bonuses_request', Scheme(VIEW_BONUSES)),
    ApiCall('view_bonuses_response', Scheme(VIEW_BONUSES_RESPONSE)),

    # lock
    ApiCall('balance_lock_request', Scheme(BALANCE_LOCK)),
    ApiCall('balance_lock_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('balance_lock_list_request', Scheme(BALANCE_LOCK_LIST)),
    ApiCall('balance_lock_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('view_balance_locks_request', Scheme(VIEW_BALANCE_LOCKS)),
    ApiCall('view_balance_locks_response', Scheme(VIEW_BALANCE_LOCKS_RESPONSE)),

    # unlock
    ApiCall('balance_unlock_request', Scheme(BALANCE_UNLOCK)),
    ApiCall('balance_unlock_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('balance_unlock_list_request', Scheme(BALANCE_UNLOCK_LIST)),
    ApiCall('balance_unlock_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    # chargeoff
    ApiCall('chargeoff_request', Scheme(CHARGEOFF)),
    ApiCall('chargeoff_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('chargeoff_list_request', Scheme(CHARGEOFF_LIST)),
    ApiCall('chargeoff_list_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('view_chargeoffs_request', Scheme(VIEW_CHARGEOFFS)),
    ApiCall('view_chargeoffs_response', Scheme(VIEW_CHARGEOFFS_RESPONSE)),

#    # product
#    ApiCall('product_status_request', Scheme(PRODUCT_STATUS)),
#    ApiCall('product_status_response', Scheme(PRODUCT_STATUS_RESPONSE)),

]
