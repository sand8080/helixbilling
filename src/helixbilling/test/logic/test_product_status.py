import unittest

from common import TestCaseWithBalance

from helixbilling.logic import helper
from helixbilling.logic.actions import handle_action
import helixbilling.logic.product_status as product_status


class ProductStatusTestCase(TestCaseWithBalance):
    def init_balance(self):
        self.balance.available_real_amount = 5000
        self.balance.available_virtual_amount = 0
        self.balance.overdraft_limit = 7000
        self.balance = self.update_balance(self.balance)

    def test_product_status_locked(self):
        self.init_balance()
        lock_amount = (60, 00)
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)
        lock = self._get_lock(self.balance.client_id, data['product_id'])

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
        }
        response = handle_action('product_status', data)
        self.assertEquals(product_status.locked, response['product_status'])
        self.assertEquals(lock.locked_date, response['locked_date'])
        self.assertEquals(lock_amount, response['real_amount'])

    def test_product_status_charged_off(self):
        self.init_balance()
        lock_amount = (60, 00)
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
        }
        handle_action('chargeoff', dict(data))
        chargeoff = self._get_chargeoff(self.balance.client_id, data['product_id'])

        response = handle_action('product_status', dict(data))
        self.assertEquals(product_status.charged_off, response['product_status'])
        self.assertEquals(chargeoff.locked_date, response['locked_date'])
        self.assertEquals(chargeoff.chargeoff_date, response['chargeoff_date'])
        self.assertEquals(
            lock_amount,
            self.sum_amounts([response['real_amount'], response['virtual_amount']])
        )

    def sum_amounts(self, amounts):
        total = 0
        for amount in amounts:
            total += helper.compose_amount(self.currency, *amount)
        return helper.decompose_amount(self.currency, total)

    def test_product_status_unknown(self):
        self.init_balance()
        lock_amount = (60, 00)
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'product_id': 'another product id',
        }
        response = handle_action('product_status', data)
        self.assertEquals(product_status.unknown, response['product_status'])


if __name__ == '__main__':
    unittest.main()