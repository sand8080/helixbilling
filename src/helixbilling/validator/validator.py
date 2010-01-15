from helixcore.validol.validol import Optional, AnyOf, NonNegative, Positive, Scheme, \
    Text, IsoDatetime, DecimalText
from helixcore.server.api import ApiCall

amount_validator = (NonNegative(int), NonNegative(int))
nonnegative_amount_validator = (Positive(int), NonNegative(int))
locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

PING = {}

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'category': Text(),
    'message': Text(),
}

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

AUTH_INFO = {
    'login': Text(),
    'password': Text(),
}

# --- currencies ---
VIEW_CURRENCIES = {}

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

# --- billing manager ---
ADD_BILLING_MANAGER = AUTH_INFO

MODIFY_BILLING_MANAGER = dict(
    {
        Optional('new_login'): Text(),
        Optional('new_password'): Text(),
    },
    **AUTH_INFO
)

DELETE_BILLING_MANAGER = AUTH_INFO

# --- balance ---
ADD_BALANCE = dict(
    {
        'client_id': Text(),
        'active': bool,
        'currency': Text(),
        Optional('overdraft_limit'): DecimalText(),
        Optional('locking_order'): locking_order_validator
    },
    **AUTH_INFO
)

MODIFY_BALANCE = dict(
    {
        'client_id': Text(),
        Optional('new_active'): bool,
        Optional('new_overdraft_limit'): DecimalText(),
        Optional('new_locking_order'): locking_order_validator
    },
    **AUTH_INFO
)

DELETE_BALANCE = dict(
    {
        'client_id': Text()
    },
    **AUTH_INFO
)

GET_BALANCE = dict(
    {
        'client_id': Text(),
    },
    **AUTH_INFO
)

BALANCE_INFO = {
    'client_id': Text(),
    'active': bool,
    'currency_code': Text(),
    'overdraft_limit': DecimalText(),
    'locking_order': locking_order_validator,
    'created_date': IsoDatetime(),
    'available_real_amount': DecimalText(),
    'available_virtual_amount': DecimalText(),
    'locked_amount': DecimalText(),
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
        Optional('filter'): {
            Optional('clients_ids'): [Text()],
        }
    },
    **AUTH_INFO
)

VIEW_BALANCES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        balances = [BALANCE_INFO]
    ),
    RESPONSE_STATUS_ERROR
)


# --- operations ---
ENROLL_RECEIPT = dict(
    {
        'client_id': Text(),
        'amount': nonnegative_amount_validator,
    },
    **AUTH_INFO
)

ENROLL_BONUS = dict(
    {
        'client_id': Text(),
        'amount': nonnegative_amount_validator,
    },
    **AUTH_INFO
)

LOCK_INFO = {
    'client_id': Text(),
    'product_id': Text(),
    'amount': nonnegative_amount_validator,
}

LOCK = dict(
    LOCK_INFO,
    **AUTH_INFO
)

LOCK_LIST = dict(
    {
        'locks': [LOCK_INFO]
    },
    **AUTH_INFO
)

UNLOCK_INFO = {
    'client_id': Text(),
    'product_id': Text(),
}

UNLOCK = dict(
    UNLOCK_INFO,
    **AUTH_INFO
)

UNLOCK_LIST = dict(
    {
        'unlocks': [UNLOCK_INFO]
    },
    **AUTH_INFO
)

PRODUCT_STATUS = dict(
    {
        'client_id': Text(),
        'product_id': Text(),
    },
    **AUTH_INFO
)

CHARGEOFF_INFO = {
    'client_id': Text(),
    'product_id': Text(),
}

CHARGEOFF = dict(
    CHARGEOFF_INFO,
    **AUTH_INFO
)

CHARGEOFF_LIST = dict(
    {
        'chargeoffs': [CHARGEOFF_INFO]
    },
    **AUTH_INFO
)

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

# --- view operations ---
VIEW_RECEIPTS = dict(
    {
        'client_id': Text(),
        Optional('start_date'): IsoDatetime(),
        Optional('end_date'): IsoDatetime(),
        'offset': NonNegative(int),
        'limit': Positive(int),
    },
    **AUTH_INFO
)

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

VIEW_BONUSES = dict(
    {
        'client_id': Text(),
        Optional('start_date'): IsoDatetime(),
        Optional('end_date'): IsoDatetime(),
        'offset': NonNegative(int),
        'limit': Positive(int),
    },
    **AUTH_INFO
)

VIEW_BONUSES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK,
        **{
            'total': NonNegative(int),
            'bonuses': [{
                'client_id': Text(),
                'amount': nonnegative_amount_validator,
                'created_date': IsoDatetime(),
            }],
        }
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_CHARGEOFFS = dict(
    {
        'client_id': Text(),
        Optional('product_id'): Text(),
        Optional('locked_start_date'): IsoDatetime(),
        Optional('locked_end_date'): IsoDatetime(),
        Optional('chargeoff_start_date'): IsoDatetime(),
        Optional('chargeoff_end_date'): IsoDatetime(),
        'offset': NonNegative(int),
        'limit': Positive(int),
    },
    **AUTH_INFO
)

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

VIEW_BALANCE_LOCKS = dict(
    {
        'client_id': Text(),
        Optional('product_id'): Text(),
        Optional('locked_start_date'): IsoDatetime(),
        Optional('locked_end_date'): IsoDatetime(),
        'offset': NonNegative(int),
        'limit': Positive(int),
    },
    **AUTH_INFO
)


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

    # billing manager
    ApiCall('add_billing_manager_request', Scheme(ADD_BILLING_MANAGER)),
    ApiCall('add_billing_manager_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_billing_manager_request', Scheme(MODIFY_BILLING_MANAGER)),
    ApiCall('modify_billing_manager_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_billing_manager_request', Scheme(DELETE_BILLING_MANAGER)),
    ApiCall('delete_billing_manager_response', Scheme(RESPONSE_STATUS_ONLY)),

    # currencies
    ApiCall('view_currencies_request', Scheme(VIEW_CURRENCIES)),
    ApiCall('view_currencies_response', Scheme(VIEW_CURRENCIES_RESPONSE)),

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

    ApiCall('view_bonuses_request', Scheme(VIEW_BONUSES)),
    ApiCall('view_bonuses_response', Scheme(VIEW_BONUSES_RESPONSE)),

    ApiCall('view_chargeoffs_request', Scheme(VIEW_CHARGEOFFS)),
    ApiCall('view_chargeoffs_response', Scheme(VIEW_CHARGEOFFS_RESPONSE)),

    ApiCall('view_balance_locks_request', Scheme(VIEW_BALANCE_LOCKS)),
    ApiCall('view_balance_locks_response', Scheme(VIEW_BALANCE_LOCKS_RESPONSE)),
]
