import cjson


class Authentifier(object):
    def check_access(self, session, service_type, property):
        if not self.has_access(session, service_type, property):
            raise UserAccessDenied(service_type, property)

    def has_access(self, session, service_type, property):
        data = cjson.decode(session.serialized_data)
        rights = data['rights']
        if service_type in rights:
            return property in rights[service_type]
        else:
            return False
