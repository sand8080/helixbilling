from helixbilling.test.root_test import RootTestCase

import unittest
from helixcore.server.exceptions import UnknownActionError
from helixbilling.logic.actions import handle_action


class CommonLogicTestCase(RootTestCase):
    def test_unknown_action(self):
        self.assertRaises(UnknownActionError, handle_action, 'unknown_action', {})


if __name__ == '__main__':
    unittest.main()