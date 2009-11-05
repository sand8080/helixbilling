import datetime, pytz
import unittest

from helixcore.mapping.actions import insert

from common import TestCaseWithBalance
from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import BalanceLock


class ViewBalanceLocksTestCase(TestCaseWithBalance):
    def setUp(self):
        TestCaseWithBalance.setUp(self)
        self.locked_start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        self.locked_end_date = self.locked_start_date + datetime.timedelta(days=50)

    @transaction()
    def _make_balance_lock(self, client_id, product_id, locked_date, real_amount, virtual_amount, curs=None):
        l = BalanceLock(
            client_id=client_id, product_id=product_id,
            locked_date=locked_date,
            real_amount=real_amount, virtual_amount=virtual_amount
        )
        insert(curs, l)
        return l

    def _check_balance_lock(self, obj, sel_dict):
        self.assertEquals(obj.locked_date, sel_dict['locked_date'])
        self.assertEquals(obj.product_id, sel_dict['product_id'])
        self.assertEquals(obj.real_amount, sel_dict['real_amount'][0]*100 + sel_dict['real_amount'][1])

    def test_double_balance_lock_failure(self):
        self._make_balance_lock(
            getattr(self.balance, 'client_id'), '66',
            self.locked_start_date, 789, 0
        )
        self.assertRaises(
            Exception, self._make_balance_lock,
            getattr(self.balance, 'client_id'), '66',
            self.locked_end_date, 800, 0
        )

    def test_list_balance_locks_ok(self):
        l_start = self._make_balance_lock(
            getattr(self.balance, 'client_id'), '66',
            self.locked_start_date, 789, 0
        )
        l_middle = self._make_balance_lock(
            getattr(self.balance, 'client_id'), '67',
            self.locked_start_date + datetime.timedelta(days=3), 789, 0
        )
        self._make_balance_lock(
            getattr(self.balance, 'client_id'), '68',
            self.locked_end_date + datetime.timedelta(days=3), 789, 0
        )

        data = {
            'client_id': getattr(self.balance, 'client_id'),
            'locked_start_date': self.locked_start_date.isoformat(),
            'locked_end_date': self.locked_end_date.isoformat(),
            'offset': 0,
            'limit': 10,
        }
        response = handle_action('view_balance_locks', data)
        self.assertEquals(response['total'], 2)

        selected_balance_locks = response['balance_locks']
        self.assertEquals(2, len(selected_balance_locks))
        self._check_balance_lock(l_start, selected_balance_locks[0])
        self._check_balance_lock(l_middle, selected_balance_locks[1])


if __name__ == '__main__':
    unittest.main()