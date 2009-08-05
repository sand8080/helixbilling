import cjson
from validator import validate, ValidationError

class FormatError(Exception):
    pass

def handle_request(raw_data, handler):
    '''
    Parses raw JSON request to structure, validates it and calls appropriate method on handler_object
    @param raw_data: raw JSON data.
    @param handler: callable object taking action name and parsed data as parameters.
    @raise ValidationError: if request validation fails
    @raise ValidationError: if request validation fails
    '''
    try:
        parsed_data = cjson.decode(raw_data)
    except cjson.DecodeError, e:
        raise FormatError("Cannot parse request: %s" % e)
    
    action_name = parsed_data.pop('action')
    if action_name is None:
        raise FormatError("'action' parameter is not found in request")
    
    validate(action_name, parsed_data)
    
    handler(action_name, parsed_data)
    