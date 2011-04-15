import cjson

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import get_api_calls, make_api_call

# must be imported first in helixauth set
from helixbilling.test.db_based_test import DbBasedTestCase
from helixbilling.logic import actions
from helixbilling.wsgi.protocol import protocol


class LogicTestCase(DbBasedTestCase):
    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(cjson.encode(request))
        response = actions.handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response


methods = get_api_calls(protocol)
for method_name in methods:
    setattr(LogicTestCase, method_name, make_api_call(method_name))
