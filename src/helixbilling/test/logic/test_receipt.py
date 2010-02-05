import unittest

from helixcore.mapping import actions
from helixcore.db.sql import Eq

from helixbilling.test.db_based_test import ServiceTestCase
from helixcore.server.errors import RequestProcessingError


class ReceiptTestCase(ServiceTestCase):
#    def test_enroll_receipt(self):
#        c_id = 'U0'
#        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
#        self.add_receipt(self.test_login, self.test_password, c_id, '109.01')
#        self.assertRaises(RequestProcessingError, self.add_receipt, self.test_login,
#            self.test_password, 'fake customer', '109.01')
#        self.assertRaises(RequestProcessingError, self.add_receipt, self.test_login,
#            self.test_password, c_id, '0.0')

    def test_view_receipts(self):
        c_ids = {'U0': 5, 'U1': 1, 'U2': 3, 'U3': 0}
        for c_id, rec_num in c_ids.items():
            self.add_balance(self.test_login, self.test_password, c_id, self.currency)
            for i in xrange(rec_num):
                self.add_receipt(self.test_login, self.test_password, c_id, '%s' % (i + 1))
        response = self.handle_action('view_receipts', {'login': self.test_login, 'password': self.test_password,
            'filter_params': {}, 'paging_params': {}})
        print '###', response

#    @transaction()
#    def get_receipt_total(self, client_id, curs=None):
#        return actions.get(curs, ReceiptTotalView, Eq('client_id', client_id))
#
#    def test_view(self):
#        client_one = 'one'
#        self.create_balance(client_one, self.currency)
#        self.check_view(self.get_receipt_total(client_one), {'client_id': client_one, 'amount': 0})
#
#        self.add_receipt(client_one, 50)
#        self.add_receipt(client_one, 10)
#        self.check_view(self.get_receipt_total(client_one), {'client_id': client_one, 'amount': 60})
#
#        client_two = 'two'
#        self.create_balance(client_two, self.currency)
#        self.check_view(self.get_receipt_total(client_two), {'client_id': client_two, 'amount': 0})
#        self.add_receipt(client_two, 20)
#        self.add_receipt(client_two, 70)
#        self.check_view(self.get_receipt_total(client_two), {'client_id': client_two, 'amount': 90})


if __name__ == '__main__':
    unittest.main()