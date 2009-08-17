from helixcore.validol.validol import Optional, AnyOf, NonNegative, Positive, Scheme
from helixbilling.error.errors import RequestProcessingError
import re

amount_validator = (NonNegative(int), NonNegative(int))
positive_amount_validator = (Positive(int), Positive(int))
id_validator = Positive(int)
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
    'name': AnyOf(str, unicode),
    'designation': AnyOf(str, unicode),
    Optional('cent_factor'): NonNegative(int),
}

MODIFY_CURRENCY = {
    'name': AnyOf(str, unicode),
    Optional('designation'): AnyOf(str, unicode),
    Optional('cent_factor'): NonNegative(int),
}

DELETE_CURRENCY = {
    'name': AnyOf(str, unicode),
}

# --- balance ---
CREATE_BALANCE = {
    'client_id': id_validator,
    'active': AnyOf(0, 1),
    'currency_name': AnyOf(str, unicode),
    'overdraft_limit': amount_validator,
}

MODIFY_BALANCE = {
    'client_id': id_validator,
    Optional('active'): AnyOf(0, 1),
    Optional('overdraft_limit'): amount_validator,
}

# --- operations ---
ENROLL_RECEIPT = {
    'client_id': id_validator,
    'amount': positive_amount_validator,
}

LOCK = {
    'client_id': id_validator,
    'product_id': id_validator,
    'amount': positive_amount_validator,
}

UNLOCK = {
    'client_id': id_validator,
    'product_id': id_validator,
}

PRODUCT_STATUS = {
    'client_id': id_validator,
    'product_id': id_validator,
}

MAKE_BONUS = {
    'client_id': id_validator,
    'amount': positive_amount_validator,
}

CHARGE_OFF = {
    'client_id': id_validator,
    'product_id': id_validator,
}

# --- list operations ---
LIST_RECEIPTS = {
    'client_id': id_validator,
    Optional('start_date'): iso_datetime_validator,
    Optional('end_date'): iso_datetime_validator,
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
    'make_bonus': Scheme(MAKE_BONUS),

    'lock': Scheme(LOCK),
    'unlock': Scheme(UNLOCK),

    'charge_off': Scheme(CHARGE_OFF),

    'product_status': Scheme(PRODUCT_STATUS),
    'list_receipts': Scheme(LIST_RECEIPTS),
}

class ValidationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.validation, msg)

def validate(action_name, data):
    '''
    Validates API request data by action name
    @raise ValidationError: if validation failed for some reason
    '''
    scheme = scheme = action_to_scheme_map.get(action_name)
    if scheme is None:
        raise ValidationError('Unknown action: %s' % action_name)

    result = scheme.validate(data)
    if not result:
        raise ValidationError('Validation failed for action %s' % action_name)
