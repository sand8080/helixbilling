import cjson

from helixcore.error import AuthError


class Authentifier(object):
    def __init__(self, url, port):
        self.url = url
        self.port = port

    def check_access(self, session, service_type, property):
        if not self.has_access(session, service_type, property):
            raise AuthError(service_type, property)

    def has_access(self, session, service_type, property):

        data = cjson.decode(session.serialized_data)
        rights = data['rights']
        if service_type in rights:
            return property in rights[service_type]
        else:
            return False
