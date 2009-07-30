import unittest
import psycopg2

from conf.settings import DSN
from wrapper import transaction, get_connection

class WrapperTestCase(unittest.TestCase):
    
    @transaction(get_conn=get_connection)
    def create_table(self, conn):
        print 'create table', conn
    
    def test_create_table(self):
        self.create_table()
        
#    def test_create_table(self):
#        try:
#            self.create_table(wrapper.conn)
#        except Error, e:
#            wrapper.conn.rollback()
#            raise
#        finally:
#            self.drop_table()
#            wrapper.conn.commit()
#
#    def create_table(self, conn):
#        curs = conn.cursor()
#        try:
#            curs.execute('CREATE TABLE test_create (id serial, name varchar, date timestamp)')
#        finally:
#            curs.close()
#        conn.commit()
#        
#    def drop_table(self):
#        curs = wrapper.conn.cursor()
#        try:
#            curs.execute('DROP TABLE IF EXISTS test_create')
#        finally:
#            curs.close()
#        
#    def test_transaction_scoped(self):
#        conn_1 = psycopg2.connect(DSN)
#        conn_2 = psycopg2.connect(DSN)
#        curs_1 = conn_1.cursor()
#        curs_2 = conn_2.cursor()
#        
#        try:
#            self.create_table()
        
if __name__ == '__main__':
    unittest.main()
