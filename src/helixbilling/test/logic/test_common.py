from helixbilling.test.root_test import RootTestCase

from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import UnknownActionError

class CommonLogicTestCase(RootTestCase):

    def test_unknown_action(self):
        self.assertRaises(UnknownActionError, handle_action, 'unknown_action', {})
