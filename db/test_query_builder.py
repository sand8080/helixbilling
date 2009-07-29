# -*- coding: utf-8 -*-
import unittest

from db.query_builder import quote, quote_value, quote_list
from db.query_builder import Cond, EqCond, NotCond, AndCond, OrCond, ScopedCond
from db.query_builder import select

class QueryBuilder(unittest.TestCase):
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
        
    def test_select(self):
        self.assertEqual('SELECT * FROM "billing"', select('billing'))
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"',
            select('billing', columns=['id', 'billing.amount'])
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"  GROUP BY "id","billing"."currency"',
            select('billing', columns=['id', 'billing.amount'], group_by=['id', 'billing.currency'])
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"  GROUP BY "id","billing"."currency" ORDER BY "id" DESC',
            select('billing', columns=['id', 'billing.amount'], group_by=['id', 'billing.currency'], order_by=['-', 'id'])
        )
        self.assertEqual(
            'SELECT "id","billing"."amount" FROM "billing"  GROUP BY "id","billing"."currency" ORDER BY "id","ammount" ASC',
            select('billing', columns=['id', 'billing.amount'], group_by=['id', 'billing.currency'], order_by=['id', 'ammount'])
        )
        self.assertEqual(
            'SELECT * FROM "billing"   ORDER BY "id","ammount" ASC LIMIT 4',
            select('billing', order_by=['id', 'ammount'], limit=4)
        )
        self.assertEqual(
            'SELECT * FROM "billing"   ORDER BY "id","ammount" ASC LIMIT 5 OFFSET 6',
            select('billing', order_by=['id', 'ammount'], limit=5, offset=6)
        )
        
        cond_and = AndCond(
            Cond('billing.amount', '>', 10),
            Cond('billing.amount', '<', 100)
        )
        self.assertEqual(
            'SELECT * FROM "billing" WHERE "billing"."amount" > 10 AND "billing"."amount" < 100',
            select('billing', cond=cond_and)
        )
        self.assertEqual(
            'SELECT * FROM "billing" WHERE "id" = 5     FOR UPDATE',
            select('billing', cond=EqCond('id', 5), for_update=True)
        )
         
if __name__ == '__main__':
    unittest.main()
