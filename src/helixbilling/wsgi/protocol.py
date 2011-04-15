from helixcore.server.api import ApiCall
from helixcore.json_validator import (Optional, AnyOf, NonNegative, Positive,
    Scheme, Text, NullableText, IsoDatetime, DecimalText, ArbitraryDict)
from helixcore.server.protocol_primitives import (REQUEST_PAGING_PARAMS,
    RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR, RESPONSE_STATUS_ONLY,
    AUTHORIZED_RESPONSE_STATUS_OK, AUTHORIZED_RESPONSE_STATUS_ERROR,
    AUTHORIZED_RESPONSE_STATUS_ONLY, AUTHORIZED_REQUEST_AUTH_INFO,
    ADDING_OBJECT_RESPONSE,
    PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE,
    LOGOUT_REQUEST, LOGOUT_RESPONSE)


locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

LOGIN_REQUEST = {
    'login': Text(),
    'password': Text(),
    'environment_name': Text(),
    Optional('custom_actor_info'): NullableText(),
}

LOGIN_RESPONSE = AUTHORIZED_RESPONSE_STATUS_ONLY

LOGOUT_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

LOGOUT_RESPONSE = RESPONSE_STATUS_ONLY


GET_CURRENCIES_REQUEST = {
    Optional('ordering_params'): [AnyOf('code', '-code')],
}

GET_CURRENCIES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'currencies': [
            {
                'code': Text(),
                'cent_factor': Positive(int),
                'name': Text(),
                'location': Text(),
            }
        ]}
    ),
    RESPONSE_STATUS_ERROR
)

ADD_BALANCE_REQUEST = dict(
    {
        'customer_id': Text(),
        'active': bool,
        'currency': Text(),
        Optional('overdraft_limit'): DecimalText(),
        Optional('locking_order'): locking_order_validator
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_BALANCE_RESPONSE = ADDING_OBJECT_RESPONSE

MODIFY_BALANCE_REQUEST = dict(
    {
        'customer_id': Text(),
        Optional('new_active'): bool,
        Optional('new_overdraft_limit'): DecimalText(),
        Optional('new_locking_order'): locking_order_validator
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_BALANCE_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_BALANCE_REQUEST = dict(
    {'customer_id': Text()},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_BALANCE_RESPONSE = RESPONSE_STATUS_ONLY

GET_BALANCE_REQUEST = dict(
    {'customer_id': Text()},
    **AUTHORIZED_REQUEST_AUTH_INFO
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

GET_BALANCES_REQUEST = dict(
    {
        'filter_params': {
            Optional('customer_ids'): [Text()],
        },
        'paging_params': REQUEST_PAGING_PARAMS,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_BALANCES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'balances': [BALANCE_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

## --- common income money structures ---
#ENROLL_INCOME = dict(
#    {
#        'customer_id': Text(),
#        'amount': DecimalText(),
#    },
#    **AUTH_INFO
#)
#
#VIEW_INCOMES = dict(
#    {
#        'filter_params': {
#            Optional('customer_ids'): [Text()],
#            Optional('from_creation_date'): IsoDatetime(),
#            Optional('to_creation_date'): IsoDatetime(),
#        },
#        'paging_params': PAGING_PARAMS,
#        Optional('ordering_params'): [AnyOf('creation_date', '-creation_date')]
#    },
#    **AUTH_INFO
#)
#
#INCOME_INFO = {
#    'customer_id': Text(),
#    'amount': DecimalText(),
#    'currency': Text(),
#    'creation_date': IsoDatetime(),
#}
#
#
## --- receipt ---
#ENROLL_RECEIPT = ENROLL_INCOME
#
#VIEW_RECEIPTS = VIEW_INCOMES
#
#VIEW_RECEIPTS_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'receipts': [INCOME_INFO],
#            'total': NonNegative(int),
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## ---  bonus ---
#ENROLL_BONUS = ENROLL_INCOME
#
#VIEW_BONUSES = VIEW_INCOMES
#
#VIEW_BONUSES_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'bonuses': [INCOME_INFO],
#            'total': NonNegative(int),
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## --- lock ---
#BALANCE_LOCK_DATA = {
#    'customer_id': Text(),
#    'order_id': Text(),
#    Optional('order_type'): Text(),
#    'amount': DecimalText(),
#}
#
#BALANCE_LOCK = dict(BALANCE_LOCK_DATA, **AUTH_INFO)
#
#BALANCE_LOCK_LIST = dict(
#    {'locks': [BALANCE_LOCK_DATA]},
#    **AUTH_INFO
#)
#
#VIEW_BALANCE_LOCKS = dict(
#    {
#        'filter_params': {
#            Optional('customer_ids'): [Text()],
#            Optional('order_id'): Text(),
#            Optional('order_type'): NullableText(),
#            Optional('from_locking_date'): IsoDatetime(),
#            Optional('to_locking_date'): IsoDatetime(),
#        },
#        'paging_params': PAGING_PARAMS,
#        Optional('ordering_params'): [AnyOf('locking_date', '-locking_date')]
#    },
#    **AUTH_INFO
#)
#
#VIEW_BALANCE_LOCKS_RESPONSE = AnyOf(
#    dict(RESPONSE_STATUS_OK,
#        **{
#            'balance_locks': [{
#                'customer_id': Text(),
#                'order_id': Text(),
#                'order_type': NullableText(),
#                'real_amount': DecimalText(),
#                'virtual_amount': DecimalText(),
#                'currency': Text(),
#                'locking_date': IsoDatetime(),
#            }],
#            'total': NonNegative(int),
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
## --- unlock ---
#BALANCE_UNLOCK_DATA = {
#    'customer_id': Text(),
#    'order_id': Text(),
#}
#
#BALANCE_UNLOCK = dict(BALANCE_UNLOCK_DATA, **AUTH_INFO)
#
#BALANCE_UNLOCK_LIST = dict(
#    {'unlocks': [BALANCE_UNLOCK_DATA]},
#    **AUTH_INFO
#)
#
#
## --- chargeoff ---
#CHARGEOFF_DATA = {
#    'customer_id': Text(),
#    'order_id': Text(),
#}
#
#CHARGEOFF = dict(CHARGEOFF_DATA, **AUTH_INFO)
#
#CHARGEOFF_LIST = dict(
#    {'chargeoffs': [CHARGEOFF_DATA]},
#    **AUTH_INFO
#)
#
#VIEW_CHARGEOFFS = dict(
#    {
#        'filter_params': {
#            Optional('customer_ids'): [Text()],
#            Optional('order_id'): Text(),
#            Optional('order_type'): NullableText(),
#            Optional('from_locking_date'): IsoDatetime(),
#            Optional('to_locking_date'): IsoDatetime(),
#            Optional('from_chargeoff_date'): IsoDatetime(),
#            Optional('to_chargeoff_date'): IsoDatetime(),
#        },
#        'paging_params': PAGING_PARAMS,
#        Optional('ordering_params'): [AnyOf('chargeoff_date', '-chargeoff_date')]
#    },
#    **AUTH_INFO
#)
#
#VIEW_CHARGEOFFS_RESPONSE = AnyOf(
#    dict(RESPONSE_STATUS_OK,
#        **{
#            'chargeoffs': [{
#                'customer_id': Text(),
#                'order_id': Text(),
#                'order_type': NullableText(),
#                'real_amount': DecimalText(),
#                'virtual_amount': DecimalText(),
#                'currency': Text(),
#                'locking_date': IsoDatetime(),
#                'chargeoff_date': IsoDatetime(),
#            }],
#            'total': NonNegative(int),
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## --- order ---
#ORDER_STATUS = dict(
#    {
#        'customer_id': Text(),
#        'order_id': Text(),
#    },
#    **AUTH_INFO
#)
#
#ORDER_STATUS_UNKNOWN = 'unknown'
#ORDER_STATUS_LOCKED = 'locked'
#ORDER_STATUS_CHARGED_OFF = 'charged_off'
#ORDER_STATUSES = AnyOf(ORDER_STATUS_UNKNOWN, ORDER_STATUS_LOCKED, ORDER_STATUS_CHARGED_OFF)
#
#ORDER_STATUS_DATA = {
#    'customer_id': Text(),
#    'order_id': Text(),
#    'order_status': ORDER_STATUSES,
#    'real_amount': AnyOf(None, DecimalText()),
#    'virtual_amount': AnyOf(None, DecimalText()),
#    'locking_date': AnyOf(None, IsoDatetime()),
#    'chargeoff_date': AnyOf(None, IsoDatetime()),
#}
#
#ORDER_STATUS_RESPONSE = AnyOf(
#    dict(RESPONSE_STATUS_OK,
#        **ORDER_STATUS_DATA
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_ORDER_STATUSES = dict(
#    {
#        'filter_params': {
#            Optional('customer_ids'): [Text()],
#            Optional('order_ids'): [Text()],
#            Optional('order_types'): [NullableText()],
#            Optional('from_locking_date'): IsoDatetime(),
#            Optional('to_locking_date'): IsoDatetime(),
#            Optional('from_chargeoff_date'): IsoDatetime(),
#            Optional('to_chargeoff_date'): IsoDatetime(),
#        },
#    },
#    **AUTH_INFO
#)
#
#VIEW_ORDER_STATUSES_RESPONSE = AnyOf(
#    dict(RESPONSE_STATUS_OK,
#        **{'order_statuses': [ORDER_STATUS_DATA],}
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## --- action log ---
#VIEW_ACTION_LOGS = dict(
#    {
#        'filter_params': {
#            Optional('customer_id'): Text(),
#            Optional('action'): Text(),
#            Optional('from_request_date'): IsoDatetime(),
#            Optional('to_request_date'): IsoDatetime(),
#            Optional('remote_addr'): Text(),
#        },
#        'paging_params': PAGING_PARAMS,
#    },
#    **AUTH_INFO
#)
#
#ACTION_LOG_INFO = {
#    'custom_operator_info': NullableText(),
#    'action': Text(),
#    'customer_ids': [Text()],
#    'request_date': IsoDatetime(),
#    'remote_addr': NullableText(),
#    'request': Text(),
#    'response': Text(),
#}
#
#
#VIEW_ACTION_LOGS_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'total': NonNegative(int),
#            'action_logs': [ACTION_LOG_INFO],
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)


protocol = [

    ApiCall('ping_request', Scheme(PING_REQUEST)),
    ApiCall('ping_response', Scheme(PING_RESPONSE)),

    # login user
    ApiCall('login_request', Scheme(LOGIN_REQUEST)),
    ApiCall('login_response', Scheme(LOGIN_RESPONSE)),

    # logout user
    ApiCall('logout_request', Scheme(LOGOUT_REQUEST)),
    ApiCall('logout_response', Scheme(LOGOUT_RESPONSE)),

    # currencies
    ApiCall('get_currencies_request', Scheme(GET_CURRENCIES_REQUEST)),
    ApiCall('get_currencies_response', Scheme(GET_CURRENCIES_RESPONSE)),

    # balance
    ApiCall('add_balance_request', Scheme(ADD_BALANCE_REQUEST)),
    ApiCall('add_balance_response', Scheme(ADD_BALANCE_RESPONSE)),

    ApiCall('modify_balance_request', Scheme(MODIFY_BALANCE_REQUEST)),
    ApiCall('modify_balance_response', Scheme(MODIFY_BALANCE_RESPONSE)),

    ApiCall('delete_balance_request', Scheme(DELETE_BALANCE_REQUEST)),
    ApiCall('delete_balance_response', Scheme(DELETE_BALANCE_RESPONSE)),

    ApiCall('get_balance_request', Scheme(GET_BALANCE_REQUEST)),
    ApiCall('get_balance_response', Scheme(GET_BALANCE_RESPONSE)),

    ApiCall('get_balances_request', Scheme(GET_BALANCES_REQUEST)),
    ApiCall('get_balances_response', Scheme(GET_BALANCES_RESPONSE)),

#    # receipt
#    ApiCall('enroll_receipt_request', Scheme(ENROLL_RECEIPT)),
#    ApiCall('enroll_receipt_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_receipts_request', Scheme(VIEW_RECEIPTS)),
#    ApiCall('view_receipts_response', Scheme(VIEW_RECEIPTS_RESPONSE)),
#
#    # bonus
#    ApiCall('enroll_bonus_request', Scheme(ENROLL_BONUS)),
#    ApiCall('enroll_bonus_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_bonuses_request', Scheme(VIEW_BONUSES)),
#    ApiCall('view_bonuses_response', Scheme(VIEW_BONUSES_RESPONSE)),
#
#    # lock
#    ApiCall('balance_lock_request', Scheme(BALANCE_LOCK)),
#    ApiCall('balance_lock_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('balance_lock_list_request', Scheme(BALANCE_LOCK_LIST)),
#    ApiCall('balance_lock_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_balance_locks_request', Scheme(VIEW_BALANCE_LOCKS)),
#    ApiCall('view_balance_locks_response', Scheme(VIEW_BALANCE_LOCKS_RESPONSE)),
#
#    # unlock
#    ApiCall('balance_unlock_request', Scheme(BALANCE_UNLOCK)),
#    ApiCall('balance_unlock_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('balance_unlock_list_request', Scheme(BALANCE_UNLOCK_LIST)),
#    ApiCall('balance_unlock_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    # chargeoff
#    ApiCall('chargeoff_request', Scheme(CHARGEOFF)),
#    ApiCall('chargeoff_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('chargeoff_list_request', Scheme(CHARGEOFF_LIST)),
#    ApiCall('chargeoff_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_chargeoffs_request', Scheme(VIEW_CHARGEOFFS)),
#    ApiCall('view_chargeoffs_response', Scheme(VIEW_CHARGEOFFS_RESPONSE)),
#
#    # order
#    ApiCall('order_status_request', Scheme(ORDER_STATUS)),
#    ApiCall('order_status_response', Scheme(ORDER_STATUS_RESPONSE)),
#
#    ApiCall('view_order_statuses_request', Scheme(VIEW_ORDER_STATUSES)),
#    ApiCall('view_order_statuses_response', Scheme(VIEW_ORDER_STATUSES_RESPONSE)),
#
#    # action log
#    ApiCall('view_action_logs_request', Scheme(VIEW_ACTION_LOGS)),
#    ApiCall('view_action_logs_response', Scheme(VIEW_ACTION_LOGS_RESPONSE)),

]