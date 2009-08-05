
from helixcore.db.wrapper import transaction, EmptyResultSetError
from helixcore.db.cond import Eq
from helixcore.mapping.actions import get, insert, update

from helixbilling.domain.objects import Currency

from helixbilling.logic.exceptions import  DataIntegrityError

class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    
    @transaction()
    def add_currency(self, data, curs=None):
        curr = Currency(**data)
        insert(curs, curr)
    
    @transaction()
    def modify_currency(self, data, curs=None):
        try:
            curr = get(curs, Currency, Eq('name', data['name']), True)
        except EmptyResultSetError:
            raise DataIntegrityError('Currency with name %s not found in system' % data['name'])
        
        curr.update(data)
        update(curs, curr)
    