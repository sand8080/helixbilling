import unittest

from common import ViewTestCase

from helixcore.mapping import actions
from helixcore.db.cond import Eq

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import BonusTotalView


class BonusTotalViewTestCase(ViewTestCase):
    @transaction()
    def get_bonus_total(self, client_id, curs=None):
        return actions.get(curs, BonusTotalView, Eq('client_id', client_id))

    def test_view(self):
        client_one = 'one'
        self.create_balance(client_one)
        self.check_view(self.get_bonus_total(client_one), {'client_id': client_one, 'amount': 0})

        self.add_bonus(client_one, 50)
        self.add_bonus(client_one, 10)
        self.check_view(self.get_bonus_total(client_one), {'client_id': client_one, 'amount': 60})

        client_two = 'two'
        self.create_balance(client_two)
        self.check_view(self.get_bonus_total(client_two), {'client_id': client_two, 'amount': 0})
        self.add_bonus(client_two, 20)
        self.add_bonus(client_two, 70)
        self.check_view(self.get_bonus_total(client_two), {'client_id': client_two, 'amount': 90})


if __name__ == '__main__':
    unittest.main()