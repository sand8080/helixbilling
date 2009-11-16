from helixbilling.domain.objects import Currency
import unittest

from common import LogicTestCase
from helixbilling.logic.actions import handle_action


class ViewCurrencyTestCase(LogicTestCase):
    def test_view_currencyes(self):
        response = handle_action('view_currencies', {})
        self.assertTrue('status' in response)
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        self.assertTrue(len(currencies_data) > 0)
        Currency(**currencies_data[0])


if __name__ == '__main__':
    unittest.main()