from helixcore import mapping
from helixcore.server.wsgi_application import Application

from helixbilling.conf.db import transaction
from helixbilling.db.dataobject import ActionLog


class HelixbillingApplication(Application):
    def __init__(self, h, p, l):
        tracking_api_calls = ('modify_used_currencies',
            'add_balance', 'modify_balance')
        super(HelixbillingApplication, self).__init__(h, p, l, tracking_api_calls)

    @transaction()
    def track_api_call(self, remote_addr, s_req, s_resp,
        action_name, processed_data, curs=None):
        super(HelixbillingApplication, self).track_api_call(remote_addr, s_req, s_resp,
            action_name, processed_data)

        actor_user_id = processed_data.get('actor_user_id')
        custom_actor_info = processed_data.get('custom_actor_info')
        environment_id = processed_data.get('environment_id')
        users_ids = processed_data.get('subject_users_ids', [])
        session_id = processed_data.get('session_id')

        data = {
            'environment_id': environment_id,
            'session_id': session_id,
            'custom_actor_info': custom_actor_info,
            'actor_user_id': actor_user_id,
            'subject_users_ids': users_ids,
            'action': action_name,
            'remote_addr': remote_addr,
            'request': s_req,
            'response': s_resp,
        }
        mapping.insert(curs, ActionLog(**data))
