from helixcore.security import Session

from helixbilling.test.logic.logic_test import LogicTestCase
from helixbilling.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)
