import unittest

from common import ViewTestCase

from helixcore.mapping import actions
from helixcore.db.sql import Eq

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import ChargeoffTotalView


class ChargeoffTotalViewTestCase(ViewTestCase):
    @transaction()
    def get_chargeoff_total(self, client_id, curs=None):
        return actions.get(curs, ChargeoffTotalView, Eq('client_id', client_id))

    def test_view(self):
        client_one = 'one'
        self.create_balance(client_one, self.currency)
        self.check_view(
            self.get_chargeoff_total(client_one),
            {'client_id': client_one, 'real_amount': 0, 'virtual_amount': 0}
        )

        self.add_chargeoff(client_one, 'pid1', 50, 5)
        self.add_chargeoff(client_one, 'pid2', 10, 90)
        self.check_view(
            self.get_chargeoff_total(client_one),
            {'client_id': client_one, 'real_amount': 60, 'virtual_amount': 95}
        )

        client_two = 'two'
        self.create_balance(client_two, self.currency)
        self.check_view(self.get_chargeoff_total(
            client_two),
            {'client_id': client_two, 'real_amount': 0, 'virtual_amount': 0}
        )
        self.add_chargeoff(client_two, 'pid3', 20, 11)
        self.add_chargeoff(client_two, 'pid4', 70, 12)
        self.check_view(
            self.get_chargeoff_total(client_two),
            {'client_id': client_two, 'real_amount': 90, 'virtual_amount': 23}
        )


if __name__ == '__main__':
    unittest.main()