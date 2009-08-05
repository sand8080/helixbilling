
from helixbilling.logic.exceptions import UnknownActionError
from helixbilling.logic.handler import Handler

def handle_action(action_name, data):
    '''
    Handles API action.
    @param action_name: name of API action
    @param data: dict with supplied data
    @raise UnknownActionError: if action with such name is unknown to handler
    @raise DataIntegrityError: if given data is semantically not correct
    '''
    h = Handler()
    try:
        method = getattr(h, action_name)
        method(data)
    except AttributeError:
        raise UnknownActionError('Cannot handle action %s: unknown action' % action_name)