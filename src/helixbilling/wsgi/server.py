from eventlet import api, wsgi

from helixcore.server.wsgi_application import Application

from helixbilling.conf import settings
from helixbilling.conf.log import logger
from helixbilling.logic.actions import handle_action
from helixbilling.validator.validator import api_scheme

class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.debug('server: %s' % s)

    @staticmethod
    def run():
        wsgi.server(
            api.tcp_listener((settings.server_host, settings.server_port)),
            Application(handle_action, api_scheme, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
