import unittest
import cjson

from helixbilling.api.api import handle_request, handle_response, FormatError
from helixbilling.api.validator import ValidationError


class RequestHandlingTestCase(unittest.TestCase):
    
    def test_request_format_error(self):
        raw_data = '''
        {"hren" : 8986,
        "aaa": "str", 789, -99
        }
        '''
        
        self.assertRaises(FormatError, handle_request, raw_data)
    
    def test_request_validation_error(self):
        bad_data = {
            'action': 'unknown',
            'aaa': 'str',
            'param2': 'foo bar',
        }
        
        raw_data = cjson.encode(bad_data)
        self.assertRaises(ValidationError, handle_request, raw_data)
    
    def test_add_currency(self):
        good_data = {
            'action': 'add_currency',
            'name': 'USD',
            'designation': '$',
            'cent_factor': 100,
        }
        
        raw_data = cjson.encode(good_data)
        action_name, data = handle_request(raw_data)
        self.assertEquals(action_name, good_data.pop('action'))
        self.assertEquals(data, good_data)
        
        good_response = {'status': 'ok'}
        res = cjson.decode(handle_response(good_response))
        self.assertEquals(res, good_response)

if __name__ == '__main__':
    unittest.main()
