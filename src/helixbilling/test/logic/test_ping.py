import unittest

from helixbilling.test.logic.logic_test import LogicTestCase


class PingTestCase(LogicTestCase):
    def test_ping(self):
        self.handle_action('ping', {})


if __name__ == '__main__':
    unittest.main()