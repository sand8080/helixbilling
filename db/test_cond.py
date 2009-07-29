# -*- coding: utf-8 -*-
import unittest

from db.cond import quote, quote_value, quote_list
from db.cond import Cond, EqCond, NotCond, AndCond, OrCond, ScopedCond

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
        self.assertEqual('"billing"."id" < 0', Cond('billing.id', '<', 0).glue())
        test_str = 'хитрый cat'
        self.assertEqual('"billing"."id" != \'%s\'' % test_str, Cond('billing.id', '!=', test_str).glue())
        
    def test_eq_cond(self):
        cond_end = EqCond('billing.id', 0)
        self.assertEqual('"billing"."id" = 0', cond_end.glue())
        
    def test_not_cond(self):
        cond_end = NotCond('billing.id', 'NULL')
        self.assertEqual('"billing"."id" NOT NULL', cond_end.glue())
        
    def test_and_cond(self):
        cond_lh = Cond('billing.id', '=', 0)
        cond_rh = Cond('billing.cd', '!=', 1)
        cond_end = AndCond(cond_lh, cond_rh)
        self.assertEqual('"billing"."id" = 0 AND "billing"."cd" != 1', cond_end.glue())
        
    def test_or_cond(self):
        cond_lh = Cond('billing.id', '=', 0)
        cond_rh = Cond('billing.cd', '!=', 1)
        cond_end = OrCond(cond_lh, cond_rh)
        self.assertEqual('"billing"."id" = 0 OR "billing"."cd" != 1', cond_end.glue())
        
    def test_scoped_cond(self):
        cond_lh = Cond('billing.id', '=', 'a')
        cond_rh = Cond('billing.cd', '!=', 'b')
        cond_and = AndCond(cond_lh, cond_rh)
        cond_end = ScopedCond(cond_and)
        self.assertEqual('("billing"."id" = \'a\' AND "billing"."cd" != \'b\')', cond_end.glue())
     
if __name__ == '__main__':
    unittest.main()
