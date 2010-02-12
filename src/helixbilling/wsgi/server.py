import logging
from eventlet import wsgi
from eventlet.green import socket

from helixcore.server.wsgi_application import Application
import helixcore.mapping.actions as mapping
from helixcore.utils import filter_dict

from helixbilling.conf import settings
from helixbilling.conf.log import logger
from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic import selector
from helixbilling.validator.validator import protocol
from helixbilling.domain.objects import ActionLog
from helixbilling.error import ObjectNotFound


class HelixbillingApplication(Application):
    def __init__(self, h, p, l):
        self.unauthorized_trackable = ['add_operator']
        super(HelixbillingApplication, self).__init__(h, p, l, (
            'add_operator', 'modify_operator', 'delete_operator',
            'add_balance', 'modify_balance', 'delete_balance',
            'enroll_receipt', 'enroll_bonus',
            'balance_lock', 'balance_unlock', 'chargeoff',
            'balance_lock_list', 'balance_unlock_list', 'chargeoff_list',
        ))

    @transaction()
    def track_api_call(self, remote_addr, s_req, s_resp, authorized_data, curs=None): #IGNORE:W0221
        super(HelixbillingApplication, self).track_api_call(remote_addr, s_req, s_resp, authorized_data)
        action_name = authorized_data['action']
        op_id = None
        if action_name in self.unauthorized_trackable:
            try:
                login = authorized_data['login']
                op_id = selector.get_operator_by_login(curs, login).id
            except ObjectNotFound:
                self.logger.log(logging.ERROR,
                    'Unable to track action for not existed operator. Request: %s. Response: %s', (s_req, s_resp))
        else:
            op_id = authorized_data['operator_id']
        c_ids = filter_dict(('customer_id', 'customer_ids'), authorized_data).values()
        data = {
            'operator_id': op_id,
            'custom_operator_info': authorized_data.get('custom_operator_info', None),
            'customer_ids': c_ids,
            'action': action_name,
            'remote_addr': remote_addr,
            'request': s_req,
            'response': s_resp,
        }
        mapping.insert(curs, ActionLog(**data))


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        sock = socket.socket()
        sock.bind((settings.server_host, settings.server_port))
        sock.listen(settings.server_connections)
        wsgi.server(
            sock,
            HelixbillingApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
