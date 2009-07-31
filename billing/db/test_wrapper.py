import unittest
import psycopg2
from time import sleep
from datetime import datetime

from conf.settings import DSN
from wrapper import transaction, get_connection, fetchall_dicts, fetchone_dict, dict_from_lists

class WrapperTestCase(unittest.TestCase):

    table = 'test_wrapper'
    
    def setUp(self):
        try:
            self.create_table()
        except psycopg2.Error:
            pass
    
    def tearDown(self):
        self.drop_table()

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
    def test_fetchall_dicts(self, curs=None):
        num_records = 4
        self.fill_table(num_records=num_records)
        curs.execute('SELECT * FROM %s' % self.table)
        result = fetchall_dicts(curs)
        self.assertEqual(num_records, len(result))
        data = result[0]
        self.assertEqual(3, len(data))
        self.assertTrue('id' in data)
        self.assertTrue('name' in data)
        self.assertTrue('date' in data)

    @transaction()
    def test_fetchall_dicts_not_found(self, curs=None):
        curs.execute('SELECT * FROM %s' % self.table)
        self.assertEqual(0, len(fetchall_dicts(curs)))

    @transaction()
    def test_fetchone_dict(self, curs=None):
        self.fill_table(num_records=4)
        curs.execute('SELECT * FROM %s WHERE id=%d' % (self.table, 1))
        fetchone_dict(curs)
        
    def test_fetchone_dict_raise(self):
        conn = get_connection()
        curs = conn.cursor()
        try:
            curs.execute('SELECT * FROM %s WHERE id=%d' % (self.table, 1))
            self.assertRaises(psycopg2.ProgrammingError, fetchone_dict, curs)
            curs.close()
            conn.commit()
        except:
            curs.close()
            conn.rollback()

    @transaction()
    def create_table(self, curs=None):
        curs.execute(
            'CREATE TABLE %s (id serial, name varchar, date timestamp)' %
            self.table
        )

    @transaction()
    def drop_table(self, curs=None):
        curs.execute('DROP TABLE IF EXISTS %s' % self.table)

    @transaction()
    def fill_table(self, num_records=5, curs=None):
        for i in xrange(num_records):
            curs.execute(
                'INSERT INTO ' + self.table + ' (name, date) VALUES (%(name)s, %(date)s)',
                {'name': i, 'date': datetime.now()}
            )

    def do_fetchall_dicts(self, curs=None):
        curs.execute('SELECT * FROM %s' % self.table)
        return fetchall_dicts(curs)
    
    @transaction()
    def test_dict_from_list(self, curs=None):
        num_records = 7
        self.fill_table(num_records)
        curs.execute('SELECT * FROM %s' % self.table)
        self.assertEqual(num_records, len(fetchall_dicts(curs)))

    @transaction()
    def slow_task(self, report, id, pause, curs=None):
        curs.execute('SELECT * FROM %s WHERE id=%d FOR UPDATE' % (self.table, id))
        curs.execute("UPDATE %s SET name='%s' WHERE id=%d" % (self.table, 'substituted', id))
        curs.execute('SELECT * FROM %s WHERE id=%d' % (self.table, id))
        report['slow_task'] = fetchone_dict(curs)
        sleep(pause)

    def fast_task(self, report, id, pause, conn=None):
        curs = conn.cursor()
        try:
            sleep(pause)
            curs.execute('SELECT * FROM %s WHERE id=%d' % (self.table, id))
            report['fast_task'] = fetchone_dict(curs)
            curs.close()
            conn.commit()
        except:
            curs.close()
            conn.rollback()

    @transaction()
    def task_wait_before(self, report, id, pause, curs=None):
        sleep(pause)
        curs.execute('SELECT * FROM %s WHERE id=%d FOR UPDATE' % (self.table, id))
        report['task_wait_before'] = fetchone_dict(curs)

    def test_data_isolation(self):
        self.fill_table()
        from threading import Thread
        report = {}
        id = 1
        t_slow = Thread(target=self.slow_task, args=(report, id, 0.5))
        t_fast = Thread(target=self.fast_task, args=(report, id, 0.25, get_connection()))
        t_slow.start()
        t_fast.start()
        t_slow.join()
        self.assertNotEqual(report['slow_task']['name'], report['fast_task']['name'])
    
    def test_data_consistency(self):
        self.fill_table()
        from threading import Thread
        report = {}
        id = 1
        t_one = Thread(target=self.slow_task, args=(report, id, 0.5))
        t_two = Thread(target=self.task_wait_before, args=(report, id, 0.25))
        t_one.start()
        t_two.start()
        t_one.join()
        t_two.join()
        self.assertEqual(report['slow_task']['name'], report['task_wait_before']['name'])

if __name__ == '__main__':
    unittest.main()
