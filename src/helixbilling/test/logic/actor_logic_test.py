from helixcore.security import Session

from helixbilling.test.logic.logic_test import LogicTestCase


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', 77, 79)
