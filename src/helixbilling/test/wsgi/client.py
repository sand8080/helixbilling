from helixcore.test.util import ClientApplication


class Client(ClientApplication):
    def __init__(self, host, port, login, password, protocol='http'):
        super(Client, self).__init__(host, port, login, password, protocol=protocol)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


for func_name in ['ping', 'add_balance']:
    setattr(Client, func_name, make_api_call(func_name))
