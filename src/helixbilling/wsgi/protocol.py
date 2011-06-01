from helixcore.server.api import ApiCall
from helixcore.json_validator import (Optional, AnyOf, NonNegative, Positive,
    Scheme, Text, NullableText, IsoDatetime, DecimalText, PositiveDecimalText,
    ArbitraryDict)
from helixcore.server.protocol_primitives import (REQUEST_PAGING_PARAMS,
    RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR, RESPONSE_STATUS_ONLY,
    AUTHORIZED_REQUEST_AUTH_INFO,
    ADDING_OBJECT_RESPONSE,
    PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE,
    LOGOUT_REQUEST, LOGOUT_RESPONSE)


locking_order_validator = AnyOf(None, [AnyOf('real_amount', 'virtual_amount')])

GET_CURRENCIES_REQUEST = dict(
    {
        Optional('ordering_params'): [AnyOf('code', '-code')],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CURRENCY_INFO = {
    'id': int,
    'code': Text(),
    'cent_factor': Positive(int),
    'name': Text(),
    'location': Text(),
}

GET_CURRENCIES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'currencies': [CURRENCY_INFO]}
    ),
    RESPONSE_STATUS_ERROR
)

GET_USED_CURRENCIES_REQUEST = GET_CURRENCIES_REQUEST

GET_USED_CURRENCIES_RESPONSE = GET_CURRENCIES_RESPONSE

MODIFY_USED_CURRENCIES_REQUEST = dict(
    {
        Optional('new_currencies_codes'): [Text()],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USED_CURRENCIES_RESPONSE = RESPONSE_STATUS_ONLY

ACTION_LOG_INFO = {
    'id': int,
    'session_id': NullableText(),
    'custom_actor_info': NullableText(),
    'actor_user_id': AnyOf(int, None),
    'subject_users_ids': [int],
    'action': Text(),
    'request_date': IsoDatetime(),
    'remote_addr': Text(),
    'request': Text(),
    'response': Text(),
}

GET_ACTION_LOGS_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
            Optional('user_id'): int,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'action_logs': [ACTION_LOG_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_ACTION_LOGS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_SELF_RESPONSE = GET_ACTION_LOGS_RESPONSE

ADD_BALANCE_REQUEST = dict(
    {
        'user_id': int,
        'currency_code': Text(),
        Optional('is_active'): bool,
        Optional('overdraft_limit'): DecimalText(),
        Optional('locking_order'): locking_order_validator,
        Optional('check_user_exist'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_BALANCE_RESPONSE = ADDING_OBJECT_RESPONSE

MODIFY_BALANCES_REQUEST = dict(
    {
        'ids': [int],
        Optional('new_is_active'): bool,
        Optional('new_overdraft_limit'): DecimalText(),
        Optional('new_locking_order'): locking_order_validator
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_BALANCES_RESPONSE = RESPONSE_STATUS_ONLY

BALANCE_INFO = {
    'id': int,
    'user_id': int,
    'is_active': bool,
    'currency_code': Text(),
    'real_amount': DecimalText(),
    'virtual_amount': DecimalText(),
    'overdraft_limit': DecimalText(),
    'locked_amount': DecimalText(),
    'locking_order': locking_order_validator,
}

GET_BALANCES_SELF_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

GET_BALANCES_SELF_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'balances': [BALANCE_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_BALANCES_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('user_id'): int,
            Optional('users_ids'): [int],
            Optional('is_active'): bool,
            Optional('currency_code'): Text(),
            Optional('from_real_amount'): DecimalText(),
            Optional('to_real_amount'): DecimalText(),
            Optional('from_virtual_amount'): DecimalText(),
            Optional('to_virtual_amount'): DecimalText(),
            Optional('from_overdraft_limit'): DecimalText(),
            Optional('to_overdraft_limit'): DecimalText(),
            Optional('from_locked_amount'): DecimalText(),
            Optional('to_locked_amount'): DecimalText(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'currency_id', '-currency_id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_BALANCES_RESPONSE = GET_BALANCES_SELF_RESPONSE

MONEY_OPERATION_REQUEST = dict(
    {
        'user_id': int,
        'currency_code': Text(),
        'amount': PositiveDecimalText(),
        Optional('info'): ArbitraryDict(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TRANSACTION_CREATION_RESPONSE = AnyOf(
    dict({'transaction_id': int}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

ADD_RECEIPT_REQUEST = MONEY_OPERATION_REQUEST

ADD_RECEIPT_RESPONSE = TRANSACTION_CREATION_RESPONSE

ADD_BONUS_REQUEST = MONEY_OPERATION_REQUEST

ADD_BONUS_RESPONSE = TRANSACTION_CREATION_RESPONSE

LOCK_REQUEST = MONEY_OPERATION_REQUEST

LOCK_RESPONSE = AnyOf(
    dict({'lock_id': int, 'transaction_id': int}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

GET_LOCKS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('user_id'): int,
            Optional('balance_id'): int,
            Optional('currency_code'): Text(),
            Optional('from_creation_date'): IsoDatetime(),
            Optional('to_creation_date'): IsoDatetime(),
            Optional('from_real_amount'): DecimalText(),
            Optional('to_real_amount'): DecimalText(),
            Optional('from_virtual_amount'): DecimalText(),
            Optional('to_virtual_amount'): DecimalText(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

LOCK_INFO = {
    'id': int,
    'user_id': int,
    'balance_id': int,
    'currency_code': Text(),
    'creation_date': IsoDatetime(),
    'real_amount': DecimalText(),
    'virtual_amount': DecimalText(),
    'info': ArbitraryDict(),
}

GET_LOCKS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'locks': [LOCK_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_LOCKS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('balance_id'): int,
            Optional('currency_code'): Text(),
            Optional('from_creation_date'): IsoDatetime(),
            Optional('to_creation_date'): IsoDatetime(),
            Optional('from_real_amount'): DecimalText(),
            Optional('to_real_amount'): DecimalText(),
            Optional('from_virtual_amount'): DecimalText(),
            Optional('to_virtual_amount'): DecimalText(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_LOCKS_SELF_RESPONSE = GET_LOCKS_RESPONSE

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

    ApiCall('get_used_currencies_request', Scheme(GET_USED_CURRENCIES_REQUEST)),
    ApiCall('get_used_currencies_response', Scheme(GET_USED_CURRENCIES_RESPONSE)),

    ApiCall('modify_used_currencies_request', Scheme(MODIFY_USED_CURRENCIES_REQUEST)),
    ApiCall('modify_used_currencies_response', Scheme(MODIFY_USED_CURRENCIES_RESPONSE)),

    # action log
    ApiCall('get_action_logs_request', Scheme(GET_ACTION_LOGS_REQUEST)),
    ApiCall('get_action_logs_response', Scheme(GET_ACTION_LOGS_RESPONSE)),

    ApiCall('get_action_logs_self_request', Scheme(GET_ACTION_LOGS_SELF_REQUEST)),
    ApiCall('get_action_logs_self_response', Scheme(GET_ACTION_LOGS_SELF_RESPONSE)),

    # balance
    ApiCall('add_balance_request', Scheme(ADD_BALANCE_REQUEST)),
    ApiCall('add_balance_response', Scheme(ADD_BALANCE_RESPONSE)),

    ApiCall('modify_balances_request', Scheme(MODIFY_BALANCES_REQUEST)),
    ApiCall('modify_balances_response', Scheme(MODIFY_BALANCES_RESPONSE)),

    ApiCall('get_balances_self_request', Scheme(GET_BALANCES_SELF_REQUEST)),
    ApiCall('get_balances_self_response', Scheme(GET_BALANCES_SELF_RESPONSE)),

    ApiCall('get_balances_request', Scheme(GET_BALANCES_REQUEST)),
    ApiCall('get_balances_response', Scheme(GET_BALANCES_RESPONSE)),

    # receipt
    ApiCall('add_receipt_request', Scheme(ADD_RECEIPT_REQUEST)),
    ApiCall('add_receipt_response', Scheme(ADD_RECEIPT_RESPONSE)),

    # bonus
    ApiCall('add_bonus_request', Scheme(ADD_BONUS_REQUEST)),
    ApiCall('add_bonus_response', Scheme(ADD_BONUS_RESPONSE)),

    # transactions

    # locks
    ApiCall('lock_request', Scheme(LOCK_REQUEST)),
    ApiCall('lock_response', Scheme(LOCK_RESPONSE)),

    ApiCall('get_locks_request', Scheme(GET_LOCKS_REQUEST)),
    ApiCall('get_locks_response', Scheme(GET_LOCKS_RESPONSE)),

    ApiCall('get_locks_self_request', Scheme(GET_LOCKS_SELF_REQUEST)),
    ApiCall('get_locks_self_response', Scheme(GET_LOCKS_SELF_RESPONSE)),

]
