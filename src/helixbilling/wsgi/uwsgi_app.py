from helixbilling.conf.log import logger
from helixbilling.logic.actions import handle_action
from helixbilling.wsgi.protocol import protocol
from helixbilling.wsgi.application import HelixbillingApplication


application = HelixbillingApplication(handle_action, protocol, logger)
