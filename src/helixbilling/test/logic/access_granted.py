from helixcore.security import auth


GRANTED_SESSION_ID = 'test_access_granted_session'
GRANTED_USER_ID = 777
GRANTED_ENV_ID = 88

def access_granted(_, __, ___, ____):
    return {'status': 'ok', 'session_id': GRANTED_SESSION_ID,
        'user_id': GRANTED_USER_ID, 'environment_id': GRANTED_ENV_ID}


def login_success(_, __):
    return {'status': 'ok', 'session_id': GRANTED_SESSION_ID}


auth.Authentifier.check_access = access_granted
auth.Authentifier.login = login_success