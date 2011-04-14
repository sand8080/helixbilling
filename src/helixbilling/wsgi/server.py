from eventlet import wsgi
from eventlet.green import socket

from helixbilling.conf import settings
from helixbilling.conf.log import logger
from helixbilling.logic.actions import handle_action
from helixbilling.wsgi.application import HelixbillingApplication
from helixbilling.wsgi.protocol import protocol


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        sock = socket.socket() #@UndefinedVariable
        sock.bind((settings.server_host, settings.server_port))
        sock.listen(settings.server_connections)
        wsgi.server(
            sock,
            HelixbillingApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
