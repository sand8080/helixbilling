import unittest
import cjson

from common import LogicTestCase

from helixcore.mapping.actions import get
from helixcore.db.cond import Eq

from helixbilling.conf.db import transaction
from helixbilling.logic.action_log import logged
from helixbilling.domain.objects import ActionLog

class ActionLogTestCase(LogicTestCase):
    simple_request = {'make': 'me', 'happy': 'now'}
    simple_response = {'status': 'ok', 'wtf': 42}

    @transaction()
    @logged
    def action_for_test(self, data, curs=None): #IGNORE:W0613
        return self.simple_response

    @transaction()
    def get_by_id(self, id, curs=None):
        return get(curs, ActionLog, Eq('id', id))

    def test_logging(self):
        self.action_for_test(self.simple_request)
        action_log = self.get_by_id(1)
        self.assertEqual(self.simple_request, cjson.decode(action_log.request))
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))

if __name__ == '__main__':
    unittest.main()