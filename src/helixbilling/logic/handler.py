
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.cond import Eq
from helixcore.mapping.actions import get, insert, update, delete

from helixbilling.conf.db import transaction

from helixbilling.domain.objects import Currency, Balance, Receipt
from helixbilling.logic.exceptions import  DataIntegrityError
from helixbilling.logic.response import response_ok

from helper import get_currency_by_name, get_currency_by_balance, get_balance, compose_amount, decompose_amount 

class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    
    def ping(self, data): #IGNORE:W0613
        return response_ok()
    
    # --- currency ---
    
    @transaction()
    def add_currency(self, data, curs=None):
        curr = Currency(**data)
        insert(curs, curr)
        return response_ok()
    
    @transaction()
    def modify_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)
        curr.update(data)
        update(curs, curr)
        return response_ok()
    
    @transaction()
    def delete_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)        
        delete(curs, curr)
        return response_ok()
    
    # --- balance ---
    
    @transaction()
    def create_balance(self, data, curs=None):
        currency = get_currency_by_name(curs, data['currency_name'], False)
        
        del data['currency_name']
        data['currency_id'] = currency.id
        data['overdraft_limit'] = compose_amount(currency, *data['overdraft_limit'])
        balance = Balance(**data)
        insert(curs, balance)
        return response_ok()
    
    @transaction()
    def modify_balance(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=True)
        
        if 'overdraft_limit' in data:
            currency = get_currency_by_balance(curs, balance)
            data['overdraft_limit'] = compose_amount(currency, *data['overdraft_limit'])
        
        balance.update(data)
        update(curs, balance)
        return response_ok()
    
    @transaction()
    def enroll_receipt(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)
        
        data['amount'] = compose_amount(currency, *data['amount'])
        
        receipt = Receipt(*data)
        insert(curs, receipt)
        
        balance.available_amount += receipt.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()
