import unittest

from db.cond import AndCond, Cond, EqCond
from db.query_builder import select, update, delete, insert

class QueryBuilderTestCase(unittest.TestCase):
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
            'SELECT * FROM "billing"    LIMIT 0',
            select('billing', limit=0)
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

    def test_update(self):
        self.assertEqual(
            'UPDATE "balance" SET "currency" = \'rur\',"client_id" = 4 WHERE "id" = 1',
            update('balance', {'client_id': 4, 'currency': 'rur'}, EqCond('id', 1))
        )

    def test_delete(self):
        self.assertEqual(
            'DELETE FROM "balance_lock" WHERE "balance_id" = 7',
            delete('balance_lock', EqCond('balance_id', 7))
        )

    def test_insert(self):
        self.assertEqual(
            'INSERT INTO "balance" ("currency","amount","client_id") VALUES (\'usd\',0,42)',
            insert('balance', {'client_id': 42, 'amount': 0, 'currency': 'usd'})
        )

if __name__ == '__main__':
    unittest.main()
