from helixcore.server.api import ApiCall
from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Scheme, Text, NullableText, IsoDatetime, DecimalText, PositiveDecimalText,
    ArbitraryDict)
from helixcore.server.protocol_primitives import (REQUEST_PAGING_PARAMS,
    RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR, RESPONSE_STATUS_ONLY,
    AUTHORIZED_REQUEST_AUTH_INFO,
    ADDING_OBJECT_RESPONSE,
    PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE,
    LOGOUT_REQUEST, LOGOUT_RESPONSE, GET_ACTION_LOGS_REQUEST,
    GET_ACTION_LOGS_RESPONSE, GET_ACTION_LOGS_SELF_REQUEST,
    GET_ACTION_LOGS_SELF_RESPONSE, GET_CURRENCIES_REQUEST,
    GET_CURRENCIES_RESPONSE)


locking_order_validator = AnyOf(None, [AnyOf('real_amount', 'virtual_amount')])
transaction_type_validator = AnyOf('receipt', 'bonus', 'lock', 'unlock', 'charge_off')


GET_USED_CURRENCIES_REQUEST = GET_CURRENCIES_REQUEST

GET_USED_CURRENCIES_RESPONSE = GET_CURRENCIES_RESPONSE

MODIFY_USED_CURRENCIES_REQUEST = dict(
    {
        Optional('new_currencies_codes'): [Text()],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USED_CURRENCIES_RESPONSE = RESPONSE_STATUS_ONLY

ADD_BALANCE_REQUEST = dict(
    {
        'user_id': int,
        'currency_code': Text(),
        Optional('is_active'): bool,
        Optional('overdraft_limit'): DecimalText(),
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
        'balance_id': int,
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

LOCK_REQUEST = dict(MONEY_OPERATION_REQUEST)
LOCK_REQUEST['locking_order'] = locking_order_validator
LOCK_REQUEST['order_id'] = NullableText()

LOCK_RESPONSE = AnyOf(
    dict({'lock_id': int, 'transaction_id': int}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

LOCK_INFO = {
    'id': int,
    'user_id': int,
    'balance_id': int,
    'currency_code': Text(),
    'creation_date': IsoDatetime(),
    'real_amount': DecimalText(),
    'virtual_amount': DecimalText(),
    'order_id': NullableText(),
    'info': ArbitraryDict(),
}

GET_LOCKS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('balance_id'): int,
            Optional('order_id'): Text(),
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

GET_LOCKS_SELF_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'locks': [LOCK_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_LOCKS_REQUEST = GET_LOCKS_SELF_REQUEST
GET_LOCKS_REQUEST['filter_params'][Optional('user_id')] = int

GET_LOCKS_RESPONSE = GET_LOCKS_SELF_RESPONSE

UNLOCK_REQUEST = dict(
    {
        'balance_id': int,
        'lock_id': int,
        Optional('info'): ArbitraryDict(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

UNLOCK_RESPONSE = AnyOf(
    dict({'transaction_id': int}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

CHARGE_OFF_REQUEST = UNLOCK_REQUEST

CHARGE_OFF_RESPONSE = UNLOCK_RESPONSE

TRANSACTION_INFO = {
    'id': int,
    'user_id': int,
    'balance_id': int,
    'currency_code': Text(),
    'real_amount': DecimalText(),
    'virtual_amount': DecimalText(),
    'order_id': NullableText(),
    'creation_date': IsoDatetime(),
    'type': Text(),
    'info': ArbitraryDict(),
}

GET_TRANSACTIONS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('balance_id'): int,
            Optional('order_id'): Text(),
            Optional('from_creation_date'): IsoDatetime(),
            Optional('to_creation_date'): IsoDatetime(),
            Optional('type'): transaction_type_validator,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_TRANSACTIONS_SELF_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'transactions': [TRANSACTION_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_TRANSACTIONS_REQUEST = dict(GET_TRANSACTIONS_SELF_REQUEST)
GET_TRANSACTIONS_REQUEST['filter_params'][Optional('user_id')] = int

GET_TRANSACTIONS_RESPONSE = GET_TRANSACTIONS_SELF_RESPONSE

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
    ApiCall('get_transactions_request', Scheme(GET_TRANSACTIONS_REQUEST)),
    ApiCall('get_transactions_response', Scheme(GET_TRANSACTIONS_RESPONSE)),

    ApiCall('get_transactions_self_request', Scheme(GET_TRANSACTIONS_SELF_REQUEST)),
    ApiCall('get_transactions_self_response', Scheme(GET_TRANSACTIONS_SELF_RESPONSE)),

    # balance amount decreasing
    ApiCall('lock_request', Scheme(LOCK_REQUEST)),
    ApiCall('lock_response', Scheme(LOCK_RESPONSE)),

    ApiCall('get_locks_request', Scheme(GET_LOCKS_REQUEST)),
    ApiCall('get_locks_response', Scheme(GET_LOCKS_RESPONSE)),

    ApiCall('get_locks_self_request', Scheme(GET_LOCKS_SELF_REQUEST)),
    ApiCall('get_locks_self_response', Scheme(GET_LOCKS_SELF_RESPONSE)),

    ApiCall('unlock_request', Scheme(UNLOCK_REQUEST)),
    ApiCall('unlock_response', Scheme(UNLOCK_RESPONSE)),

    ApiCall('charge_off_request', Scheme(CHARGE_OFF_REQUEST)),
    ApiCall('charge_off_response', Scheme(CHARGE_OFF_RESPONSE)),

]
