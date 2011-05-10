from helixcore.security import auth


GRANTED_SESSION_ID = 'test_access_granted_session'
GRANTED_USER_ID = '777'
GRANTED_ENV_ID = '88'

resp = {'status': 'ok', 'session_id': GRANTED_SESSION_ID,
    'user_id': GRANTED_USER_ID, 'environment_id': GRANTED_ENV_ID}

def access_granted(_, __, ___, ____):
    return resp


def login_success(_, __):
    return resp


def logout_success(_, __):
    return {'status': 'ok'}


auth.CoreAuthenticator.check_access = access_granted
auth.CoreAuthenticator.login = login_success
auth.CoreAuthenticator.logout = logout_success
