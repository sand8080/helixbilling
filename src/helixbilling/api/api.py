import cjson
from validator import validate
from helixbilling.error.errors import RequestProcessingError

class FormatError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.request_format, msg)

def handle_request(raw_data):
    '''
    Parses raw JSON request to structure, validates it and calls appropriate method on handler_object
    @param raw_data: raw JSON data.
    @param handler: callable object taking action name and parsed data as parameters. Returns response dict
    @return: tuple(action_name, data_dict)
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
    
    return (action_name, parsed_data)
    
def handle_response(response_dict):
    '''
    Validates (custom operation) and encodes response dict
    @param response_dict: response data.
    @param handler: callable object taking action name and parsed data as parameters. Returns response dict
    @raise ValidationError: if request validation fails
    @return: raw encoded response
    '''
    return cjson.encode(response_dict)
    
