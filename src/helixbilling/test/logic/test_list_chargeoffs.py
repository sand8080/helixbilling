import datetime, pytz
import unittest

from helixcore.mapping.actions import insert

from common import TestCaseWithBalance
from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import ChargeOff


class ListChargeoffsTestCase(TestCaseWithBalance):
    good_chargeoffs = None
    locked_start_date = None
    locked_end_date = None
    chargedoff_start_date = None
    chargedoff_end_date = None

    def setUp(self):
        TestCaseWithBalance.setUp(self)
        self._create_chargeoffs()

    def _create_chargeoffs(self):
        locked_start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        locked_end_date = locked_start_date + datetime.timedelta(days=70)

        chargedoff_start_date = datetime.datetime(2009, 6, 1, tzinfo=pytz.utc)
        chargedoff_end_date = chargedoff_start_date + datetime.timedelta(days=70)

        # other client
        self._make_chargeoff(
            '899',
            '44',
            locked_start_date,
            chargedoff_start_date,
            5099, 0
        )
        self._make_chargeoff(
            self.balance.client_id, #IGNORE:E1101
            '45',
            datetime.datetime(2009, 2, 21, tzinfo=pytz.utc),
            datetime.datetime(2009, 3, 21, tzinfo=pytz.utc),
            5000, 0
        )
        self.good_chargeoffs = (
            self._make_chargeoff(
                self.balance.client_id,  #IGNORE:E1101
                '70',
                locked_start_date,
                chargedoff_start_date,
                6200, 0
            ),
            self._make_chargeoff(
                self.balance.client_id, #IGNORE:E1101
                '71',
                locked_start_date + datetime.timedelta(days=3),
                chargedoff_start_date + datetime.timedelta(days=3),
                7060, 0
            ),
            self._make_chargeoff(
                self.balance.client_id,  #IGNORE:E1101
                '72',
                locked_end_date - datetime.timedelta(seconds=1),
                chargedoff_end_date - datetime.timedelta(seconds=1),
                7899, 0
            )
        )
        # too late
        self._make_chargeoff(
            self.balance.client_id, #IGNORE:E1101
            '46',
            locked_end_date,
            chargedoff_end_date,
            1080, 0
        )
        self.locked_start_date = locked_start_date
        self.locked_end_date = locked_end_date
        self.chargedoff_start_date = chargedoff_start_date
        self.chargedoff_end_date = chargedoff_end_date

    @transaction()
    def _make_chargeoff(self, client_id, product_id, locked_date, chargeoff_date, real_amount, virtual_amount, curs=None):
        chargeoff = ChargeOff(
            client_id=client_id, product_id=product_id,
            locked_date=locked_date, chargeoff_date=chargeoff_date,
            real_amount=real_amount,
            virtual_amount=virtual_amount
        ) #IGNORE:E1101
        insert(curs, chargeoff)
        return chargeoff

    def _check_chargeoff(self, chargeoff_obj, sel_dict):
        self.assertEquals(chargeoff_obj.client_id, sel_dict['client_id'])
        self.assertEquals(chargeoff_obj.product_id, sel_dict['product_id'])
        self.assertEquals(chargeoff_obj.locked_date, sel_dict['locked_date'])
        self.assertEquals(chargeoff_obj.chargeoff_date, sel_dict['chargeoff_date'])
        self.assertEquals(chargeoff_obj.real_amount, sel_dict['real_amount'][0]*100 + sel_dict['real_amount'][1])
        self.assertEquals(chargeoff_obj.virtual_amount, sel_dict['virtual_amount'][0]*100 + sel_dict['virtual_amount'][1])

    def test_list_chargeoffs_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'locked_start_date': self.locked_start_date.isoformat(),
            'locked_end_date': self.locked_end_date.isoformat(),
            'chargedoff_start_date': self.locked_start_date.isoformat(),
            'chargedoff_end_date': self.locked_end_date.isoformat(),
            'offset': 0,
            'limit': 10,
        }

        output = handle_action('list_chargeoffs', data)
        self.assertEquals(3, output['total'])

        selected_chargeoffs = output['chargeoffs']
        self.assertEquals(3, len(selected_chargeoffs))

        for i, c in enumerate(self.good_chargeoffs):
            self._check_chargeoff(c, selected_chargeoffs[i])

    def test_list_chargeoffs_paged(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'locked_start_date': self.locked_start_date.isoformat(),
            'locked_end_date': self.locked_end_date.isoformat(),
            'chargedoff_start_date': self.locked_start_date.isoformat(),
            'chargedoff_end_date': self.locked_end_date.isoformat(),
            'offset': 0,
            'limit': 2,
        }

        output = handle_action('list_chargeoffs', data)
        self.assertEquals(3, output['total'])

        selected_chargeoffs = output['chargeoffs']
        self.assertEquals(data['limit'], len(selected_chargeoffs))

        for i in xrange(data['limit']):
            self._check_chargeoff(self.good_chargeoffs[i], selected_chargeoffs[i])

        data['offset'] = 2
        data['limit'] = 20
        output = handle_action('list_chargeoffs', data)
        self.assertEquals(output['total'], 3)

        selected_chargeoffs = output['chargeoffs']
        self.assertEquals(1, len(selected_chargeoffs))
        self._check_chargeoff(self.good_chargeoffs[2], selected_chargeoffs[0])

if __name__ == '__main__':
    unittest.main()