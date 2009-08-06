
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.cond import Eq
from helixcore.mapping.actions import get, insert, update, delete

from helixbilling.conf.db import transaction

from helixbilling.domain.objects import Currency
from helixbilling.logic.exceptions import  DataIntegrityError
from helixbilling.logic.response import response_ok

class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    
    def ping(self, data): #IGNORE:W0613
        return response_ok()
        
    @transaction()
    def add_currency(self, data, curs=None):
        curr = Currency(**data)
        insert(curs, curr)
        return response_ok()
    
    @transaction()
    def modify_currency(self, data, curs=None):
        try:
            curr = get(curs, Currency, Eq('name', data['name']), True)
        except EmptyResultSetError:
            raise DataIntegrityError('Currency with name %s not found in system' % data['name'])
        
        curr.update(data)
        update(curs, curr)
        return response_ok()
    
    @transaction()
    def delete_currency(self, data, curs=None):
        try:
            curr = get(curs, Currency, Eq('name', data['name']), True)
        except EmptyResultSetError:
            raise DataIntegrityError('Currency with name %s not found in system' % data['name'])
        
        delete(curs, curr)
        return response_ok()
    