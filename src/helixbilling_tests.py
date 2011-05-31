import unittest

from helixbilling.test.logic.test_login import LoginTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_logout import LogoutTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_logic import LogicTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_balance import BalanceTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_currency import CurrencyTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_receipt import ReceiptTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_bonus import BonusTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_lock import BalanceLockTestCase #IGNORE:W0611 @UnusedImport
from helixbilling.test.logic.test_action_log import ActionLogTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
