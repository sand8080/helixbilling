import unittest

from common import ViewTestCase

from helixcore.mapping import actions
from helixcore.db.cond import Eq

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import ChargeoffTotalView


class ChargeoffTotalViewTestCase(ViewTestCase):
    @transaction()
    def get_chargeoff_total(self, client_id, curs=None):
        return actions.get(curs, ChargeoffTotalView, Eq('client_id', client_id))

    def test_view(self):
        client_one = 'one'
        self.create_balance(client_one)
        self.check_view(self.get_chargeoff_total(client_one), {'client_id': client_one, 'amount': 0})

        self.add_chargeoff(client_one, 'pid1', 50)
        self.add_chargeoff(client_one, 'pid2', 10)
        self.check_view(self.get_chargeoff_total(client_one), {'client_id': client_one, 'amount': 60})

        client_two = 'two'
        self.create_balance(client_two)
        self.check_view(self.get_chargeoff_total(client_two), {'client_id': client_two, 'amount': 0})
        self.add_chargeoff(client_two, 'pid3', 20)
        self.add_chargeoff(client_two, 'pid4', 70)
        self.check_view(self.get_chargeoff_total(client_two), {'client_id': client_two, 'amount': 90})


if __name__ == '__main__':
    unittest.main()