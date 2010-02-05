import unittest

from helixbilling.domain.objects import Currency
from helixbilling.test.db_based_test import ServiceTestCase


class ViewCurrencyTestCase(ServiceTestCase):
    def test_view_currencyes(self):
        response = self.handle_action('view_currencies', {})
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        self.assertTrue(len(currencies_data) > 0)
        Currency(**currencies_data[0])


if __name__ == '__main__':
    unittest.main()