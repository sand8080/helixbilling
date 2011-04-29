from helixcore.security import Session

from helixbilling.test.logic.logic_test import LogicTestCase
from helixbilling.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)
from helixcore.db.filters import build_dicts_index


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)

    def new_used_currencies(self, currs_codes):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_currencies(**req)
        self.check_response_ok(resp)

        currs_idx = build_dicts_index(resp['currencies'], idx_field='code')
        used_currs_ids = [currs_idx[code]['id'] for code in currs_codes]

        req = {'session_id': sess.session_id, 'new_currencies_ids': used_currs_ids}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)
