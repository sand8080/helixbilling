from helixcore.validol.validol import Optional, AnyOf, NonNegative, Positive, Scheme, Text
from helixcore.server.error.errors import RequestProcessingError
import re

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

action_to_scheme_map = {
    'ping': Scheme(PING),

    'add_currency': Scheme(ADD_CURRENCY),
    'modify_currency': Scheme(MODIFY_CURRENCY),
    'delete_currency': Scheme(DELETE_CURRENCY),

    'create_balance': Scheme(CREATE_BALANCE),
    'modify_balance': Scheme(MODIFY_BALANCE),

    'enroll_receipt': Scheme(ENROLL_RECEIPT),
    'enroll_bonus': Scheme(ENROLL_BONUS),

    'lock': Scheme(LOCK),
    'lock_list': Scheme(LOCK_LIST),

    'unlock': Scheme(UNLOCK),
    'unlock_list': Scheme(UNLOCK_LIST),

    'chargeoff': Scheme(CHARGEOFF),
    'chargeoff_list': Scheme(CHARGEOFF_LIST),

    'product_status': Scheme(PRODUCT_STATUS),
    'list_receipts': Scheme(LIST_RECEIPTS),
    'list_chargeoffs': Scheme(LIST_CHARGEOFFS),
    'list_balance_locks': Scheme(LIST_BALANCE_LOCK),
}

class ValidationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.validation, msg)

def validate(action_name, data):
    '''
    Validates API request data by action name
    @raise ValidationError: if validation failed for some reason
    '''
    scheme = action_to_scheme_map.get(action_name)
    if scheme is None:
        raise ValidationError('Unknown action: %s' % action_name)

    result = scheme.validate(data)
    if not result:
        raise ValidationError(
            'Validation failed for action %s. Expected scheme: %s. Actual data: %s'
            % (action_name, scheme, data)
        )
