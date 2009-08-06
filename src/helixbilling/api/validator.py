from validol import Optional, AnyOf, Scheme
from helixbilling.error.errors import RequestProcessingError

PING = {
}

ADD_CURRENCY = {
    'name': AnyOf(str, unicode),
    'designation': AnyOf(str, unicode),
    Optional('cent_factor'): int,
}

MODIFY_CURRENCY = {
    'name': AnyOf(str, unicode),
    Optional('designation'): AnyOf(str, unicode),
    Optional('cent_factor'): int,
}

DELETE_CURRENCY = {
    'name': AnyOf(str, unicode),
}

action_to_scheme_map = {
    'ping': Scheme(PING),
    'add_currency': Scheme(ADD_CURRENCY),
    'modify_currency': Scheme(MODIFY_CURRENCY),
    'delete_currency': Scheme(DELETE_CURRENCY),
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
    