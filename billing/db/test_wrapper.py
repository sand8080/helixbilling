import unittest
import psycopg2
from time import sleep
from datetime import datetime

from conf.settings import DSN
from wrapper import transaction, get_connection, fetchall_dicts, dict_from_lists

class WrapperTestCase(unittest.TestCase):

    table = 'test_wrapper'

    def test_dict_from_lists(self):
        names = ['id', 'name', 'code']
        values = [1, 'bob', 42, 'ignorable value']
        d = dict_from_lists(names, values)
        for idx, name in enumerate(names):
            self.assertEqual(values[idx], d[name])

    def test_dict_from_lists_duplicates(self):
        dup_name = 'id'
        should_be = 42
        names = [dup_name, 'name', dup_name, 'cd', dup_name]
        values = [1, 'bob', 4, 'xexe', should_be]
        d = dict_from_lists(names, values)
        self.assertEqual(len(names) - (names.count(dup_name) - 1), len(d))
        self.assertEqual(should_be, d[dup_name])

    @transaction()
    def fetch_data(self, conn):
        curs = conn.cursor()
        curs.execute('SELECT * FROM %s' % self.table)
        result = fetchall_dicts(curs)
        curs.close()
        return result

    def test_fetchall_dicts(self):
        try:
            self.create_table()
            num_records = 4
            self.fill_table(num_records=num_records)
            result = self.fetch_data()
            self.assertEqual(num_records, len(result))
            data = result[0]
            self.assertEqual(3, len(data))
            self.assertTrue('id' in data)
            self.assertTrue('name' in data)
            self.assertTrue('date' in data)
        finally:
            self.drop_table()

    @transaction()
    def create_table(self, conn):
        curs = conn.cursor()
        try:
            curs.execute(
                'CREATE TABLE %s (id serial, name varchar, date timestamp)' %
                self.table
            )
        finally:
            curs.close()

    @transaction()
    def drop_table(self, conn):
        curs = conn.cursor()
        try:
            curs.execute('DROP TABLE IF EXISTS %s' % self.table)
        finally:
            curs.close()

    def test_table_creation(self):
        try:
            self.create_table()
        except psycopg2.Error, e:
            print e
        finally:
            self.drop_table()

    @transaction()
    def fill_table(self, num_records=5, conn=None):
        curs = conn.cursor()
        try:
            for i in xrange(num_records):
                curs.execute(
                    'INSERT INTO ' + self.table + ' (name, date) VALUES (%(name)s, %(date)s)',
                    {'name': i, 'date': datetime.now()}
                )

        finally:
            curs.close()

    @transaction()
    def task_with_trans(self, report, id, conn):
        curs = conn.cursor()
        try:
            curs.execute('SELECT * FROM %s' % self.table)
            curs.fetchall()
            print curs.description
            report[id] = 'task_with_trans'
            sleep(0.5)
        finally:
            curs.close()

    def task_no_trans(self, report, id, conn):
        report[id] = 'task_no_trans', conn

    def test_data_isolation(self):
        try:
            self.create_table()
            self.fill_table()

            from threading import Thread
            report = {}

            trans_id = 1
            no_trans_id = 2
            t_slow = Thread(target=self.task_with_trans, args=(report, trans_id))
            t_fast = Thread(target=self.task_no_trans, args=(report, no_trans_id, get_connection()))
            t_slow.start()
            t_fast.start()
            t_slow.join()

            print report
        finally:
            self.drop_table()

if __name__ == '__main__':
    unittest.main()
