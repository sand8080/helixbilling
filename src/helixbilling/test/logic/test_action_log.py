import unittest
import cjson

from common import LogicTestCase

from helixcore.mapping.actions import get
from helixcore.db.cond import Eq

from helixbilling.conf.db import transaction
from helixbilling.logic.action_log import logged, logged_bulk
from helixbilling.domain.objects import ActionLog

class ActionLogTestCase(LogicTestCase):
    simple_request = {'client_id': 'mr. Jefferson', 'make': 'me', 'happy': 'now'}
    bulk_request = {'bulk': [
            simple_request,
            simple_request,
        ]
    }
    simple_response = {'status': 'ok', 'wtf': 42}

    @transaction()
    @logged
    def action_for_test(self, data, curs=None): #IGNORE:W0613
        return self.simple_response

    @transaction()
    @logged_bulk
    def action_for_bulk_test(self, data, curs=None): #IGNORE:W0613
        return self.simple_response

    @transaction()
    def get_by_id(self, id, curs=None):
        return get(curs, ActionLog, Eq('id', id))

    def test_logging(self):
        self.action_for_test(self.simple_request)
        action_log = self.get_by_id(1)
        self.assertEqual(self.simple_request, cjson.decode(action_log.request))
        self.assertEqual([self.simple_request['client_id']], action_log.client_ids)
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))

    def test_bulk_logging(self):
        self.action_for_bulk_test(self.bulk_request)
        action_log = self.get_by_id(1)
        self.assertEqual(self.bulk_request, cjson.decode(action_log.request))
        client_ids = [d['client_id'] for d in self.bulk_request['bulk']]
        self.assertEqual(client_ids, action_log.client_ids)
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))
        self.assertEqual(self.simple_response, cjson.decode(action_log.response))


if __name__ == '__main__':
    unittest.main()