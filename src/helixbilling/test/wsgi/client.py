from helixcore.test.utils_for_testing import (ClientSimpleApplication, make_api_call,
    get_api_calls)

from helixbilling.conf.log import logger
from helixbilling.logic.actions import handle_action
from helixbilling.wsgi.protocol import protocol
from helixbilling.wsgi.application import HelixbillingApplication


class Client(ClientSimpleApplication):
    def __init__(self):
        app = HelixbillingApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app)


for method_name in get_api_calls(protocol):
    setattr(Client, method_name, make_api_call(method_name))
