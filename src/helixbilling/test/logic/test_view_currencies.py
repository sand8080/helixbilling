from helixbilling.domain.objects import Currency
import unittest

from common import LogicTestCase


class ViewCurrencyTestCase(LogicTestCase):
    def test_view_currencyes(self):
        self.add_operator(self.test_login, self.test_password)
        response = self.handle_action('view_currencies', {})
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        self.assertTrue(len(currencies_data) > 0)
        Currency(**currencies_data[0])


if __name__ == '__main__':
    unittest.main()