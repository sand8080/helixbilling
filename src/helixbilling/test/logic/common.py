import unittest
import install

from helixcore.db.cond import Eq
from helixcore.mapping.actions import get, get_list, insert

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt

class LogicTestCase(unittest.TestCase):
    '''
    abstract class. All logic test cases may inherit rom this
    '''
    
    def setUp(self):
        install.execute('reinit')
        
    @transaction()
    def _add_currency(self, curs=None):
        insert(curs, Currency(name='USD', designation='$'))
    
    @transaction()
    def _get_balance(self, client_id, curs=None):
        return get(curs, Balance, Eq('client_id', client_id))
    
    @transaction()
    def _get_currency(self, name, curs=None):
        return get(curs, Currency, Eq('name', name))
    
    @transaction()
    def _get_receipts(self, client_id, curs=None):
        return get_list(curs, Receipt, Eq('client_id', client_id))
