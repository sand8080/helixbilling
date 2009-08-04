import unittest
from pprint import pformat
import cjson

from api.api import FormatError, ValidationError, handle_request


class RequestHandlingTestCase(unittest.TestCase):
    
    def test_request_format_error(self):
        raw_data = '''
        {"hren" : 8986,
        "aaa": "str", 789, -99
        }
        '''
        
        def test_handler(action_name, data): pass
        
        self.assertRaises(FormatError, handle_request, raw_data, test_handler)
    
    def test_request_validation_error(self):
        bad_data = {
            'action': 'unknown',
            'aaa': 'str',
            'param2': 'foo bar',
        }
        
        def test_handler(action_name, data): pass
        
        raw_data = cjson.encode(bad_data)
        self.assertRaises(ValidationError, handle_request, raw_data, test_handler)
    
    def test_add_currency(self):
        good_data = {
            'action': 'add_currency',
            'name': 'USD',
            'designation': '$',
            'cent_factor': 100,
        }
        
        def test_handler(action_name, data):
            self.assertEquals(action_name, good_data.pop('action'))
            self.assertEquals(data, good_data)
        
        raw_data = cjson.encode(good_data)
        handle_request(raw_data, test_handler)

if __name__ == '__main__':
   unittest.main()
   