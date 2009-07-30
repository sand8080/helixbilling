# -*- coding: utf-8 -*-
import unittest

from db.cond import quote, quote_value, quote_list
from db.cond import Cond, Eq, And, Or, Scoped

class CondTestCase(unittest.TestCase):
    def test_quote(self):
        self.assertEqual('"id"', quote('id'))
        self.assertEqual('"id"', quote('"id"'))
        self.assertEqual('""id"', quote('"id'))
        self.assertEqual('"id""', quote('id"'))
        self.assertEqual('"billing"."id"', quote('billing.id'))
        self.assertEqual('"billing"."id"', quote('"billing"."id"'))
        self.assertEqual('""billing"."id""', quote('"billing.id"'))
        self.assertEqual('"billing"."id"."cd"', quote('billing.id.cd'))

    def test_quote_value(self):
        self.assertEqual(10, quote_value(10))
        self.assertEqual("'some string'", quote_value("some string"))
        self.assertEqual("'some string'", quote_value("'some string'"))
        self.assertEqual('\'\'some string\'', quote_value("'some string"))
        self.assertEqual('\'some string\'\'', quote_value("some string'"))
        self.assertEqual("'D\'Artanian is like possum'", quote_value('D\'Artanian is like possum'))

    def test_quote_list(self):
        self.assertEqual(('"1"."1","1"."2","1"."2"."1"'), quote_list(('1.1', '1.2', '1.2.1')))

    def test_cond(self):
        self.assertEqual('"billing"."id" < 0', '%s' % Cond('billing.id', '<', 0))
        test_str = 'хитрый cat'
        self.assertEqual(
            '"billing"."id" != \'%s\'' % test_str,
            '%s' % Cond('billing.id', '!=', test_str)
        )

    def test_eq_cond(self):
        cond_end = Eq('billing.id', 0)
        self.assertEqual('"billing"."id" = 0', '%s' % cond_end)

#    def test_not_cond(self):
#        cond_end = NotCond('billing.id', 'NULL')
#        self.assertEqual('"billing"."id" NOT NULL', '%s' % cond_end)

    def test_and_cond(self):
        cond_lh = Cond('billing.id', '=', 0)
        cond_rh = Cond('billing.cd', '!=', 1)
        cond_end = And(cond_lh, cond_rh)
        self.assertEqual('"billing"."id" = 0 AND "billing"."cd" != 1', '%s' % cond_end)

    def test_or_cond(self):
        cond_lh = Cond('billing.id', '=', 0)
        cond_rh = Cond('billing.cd', '!=', 1)
        cond_end = Or(cond_lh, cond_rh)
        self.assertEqual('"billing"."id" = 0 OR "billing"."cd" != 1', '%s' % cond_end)

    def test_scoped_cond(self):
        cond_lh = Cond('billing.id', '=', 'a')
        cond_rh = Cond('billing.cd', '!=', 'b')
        cond_and = And(cond_lh, cond_rh)
        cond_end = Scoped(cond_and)
        self.assertEqual('("billing"."id" = \'a\' AND "billing"."cd" != \'b\')', '%s' % cond_end)

if __name__ == '__main__':
    unittest.main()
