import unittest

from helixbilling.domain.objects import Currency
from helixbilling.test.db_based_test import ServiceTestCase


class ViewCurrencyTestCase(ServiceTestCase):
    def test_view_currencyes(self):
        response = self.handle_action('view_currencies', {})
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        self.assertTrue(len(currencies_data) > 0)
        for d in currencies_data:
            Currency(**d)

        response = self.handle_action('view_currencies', {'ordering_params': []})
        self.assertEqual('ok', response['status'])

        response = self.handle_action('view_currencies', {'ordering_params': ['code']})
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        codes = [d['code'] for d in currencies_data]
        self.assertEqual(sorted(codes), codes)

        response = self.handle_action('view_currencies', {'ordering_params': ['-code']})
        self.assertEqual('ok', response['status'])
        currencies_data = response['currencies']
        codes = [d['code'] for d in currencies_data]
        self.assertEqual(sorted(codes, reverse=True), codes)


if __name__ == '__main__':
    unittest.main()