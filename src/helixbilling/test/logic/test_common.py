import unittest

from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import UnknownActionError

class CommonLogicTestCase(unittest.TestCase):
    
    def test_unknown_action(self):
        self.assertRaises(UnknownActionError, handle_action, 'unknown_action', {})
