import datetime, pytz
import unittest

from helixcore.mapping.actions import insert

from common import TestCaseWithBalance
from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Bonus

class ViewBonusesTestCase(TestCaseWithBalance):
    @transaction()
    def _make_bonus(self, client_id, created_date, amount, curs=None):
        bonus = Bonus(client_id=client_id, created_date=created_date, amount=amount) #IGNORE:E1101
        insert(curs, bonus)
        return bonus

    def _check_bonus(self, bonus_obj, sel_dict):
        self.assertEquals(bonus_obj.created_date, sel_dict['created_date'])
        self.assertEquals(bonus_obj.amount, sel_dict['amount'][0]*100 + sel_dict['amount'][1])

    def test_list_bonuses_ok(self):
        start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        end_date = datetime.datetime(2009, 4, 25, tzinfo=pytz.utc)

        self._make_bonus('899', datetime.datetime(2009, 1, 2, tzinfo=pytz.utc), 5099) #other client
        self._make_bonus(self.balance.client_id, datetime.datetime(2009, 2, 21, tzinfo=pytz.utc), 5000) #too early
        r_low = self._make_bonus(self.balance.client_id, start_date, 6200)
        r_mid = self._make_bonus(self.balance.client_id, datetime.datetime(2009, 4, 22, 8, 33, 44, tzinfo=pytz.utc), 7060)
        r_hi = self._make_bonus(self.balance.client_id, datetime.datetime(2009, 4, 24, 23, 59, 59, tzinfo=pytz.utc), 7060)
        self._make_bonus(self.balance.client_id, end_date, 1080) #too late

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'offset': 0,
            'limit': 10,
        }
        output = handle_action('view_bonuses', data)
        self.assertEquals(output['total'], 3)

        selected_bonuses = output['bonuses']
        self.assertEquals(len(selected_bonuses), 3)
        self._check_bonus(r_low, selected_bonuses[0])
        self._check_bonus(r_mid, selected_bonuses[1])
        self._check_bonus(r_hi, selected_bonuses[2])

    def test_list_bonuses_paged(self):
        start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        end_date = datetime.datetime(2009, 4, 25, tzinfo=pytz.utc)

        self._make_bonus('899', datetime.datetime(2009, 1, 2, tzinfo=pytz.utc), 5099) #other client
        self._make_bonus(self.balance.client_id, datetime.datetime(2009, 2, 21, tzinfo=pytz.utc), 5000) #too early
        r_low = self._make_bonus(self.balance.client_id, start_date, 6200)
        r_mid = self._make_bonus(self.balance.client_id, datetime.datetime(2009, 4, 22, 8, 33, 44, tzinfo=pytz.utc), 7060)
        r_hi = self._make_bonus(self.balance.client_id, datetime.datetime(2009, 4, 24, 23, 59, 59, tzinfo=pytz.utc), 7060)
        self._make_bonus(self.balance.client_id, end_date, 1080) #too late

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'offset': 0,
            'limit': 2,
        }
        response = handle_action('view_bonuses', dict(data))
        self.assertEquals(response['total'], 3)

        selected_bonuses = response['bonuses']
        self.assertEquals(len(selected_bonuses), 2)
        self._check_bonus(r_low, selected_bonuses[0])
        self._check_bonus(r_mid, selected_bonuses[1])

        data['offset'] = 2
        response = handle_action('view_bonuses', dict(data))
        self.assertEquals(response['total'], 3)

        selected_bonuses = response['bonuses']
        self.assertEquals(len(selected_bonuses), 1)
        self._check_bonus(r_hi, selected_bonuses[0])

    def test_list_bonuses_none(self):
        start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        end_date = datetime.datetime(2009, 4, 25, tzinfo=pytz.utc)

        self._make_bonus('899', datetime.datetime(2009, 1, 2, tzinfo=pytz.utc), 5099) #other client
        self._make_bonus(self.balance.client_id, datetime.datetime(2009, 2, 21, tzinfo=pytz.utc), 5000) #too early
        self._make_bonus(self.balance.client_id, end_date, 1080) #too late

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'offset': 0,
            'limit': 10,
        }
        response = handle_action('view_bonuses', data)
        self.assertEquals(response['total'], 0)

        selected_bonuses = response['bonuses']
        self.assertEquals(len(selected_bonuses), 0)


if __name__ == '__main__':
    unittest.main()