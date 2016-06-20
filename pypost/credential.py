from log import LOG, Logs
from getpass import getpass


class credential(object):
    def __init__(self, username, password):
        self.uname = username
        self.passwd = password

    def set_credentials_from_stdin(self):
        uname = raw_input('Username: ')
        passwd = getpass()

        self.uname = uname
        self.passwd = passwd

    def set_credentials_from_file(self, filename):
        try:
            fp = open(filename, 'r')
        except IOError:
            LOG(msg='Unable to open credential file: %s' % filename, log=Logs.ERROR)
            self.uname = None
            self.passwd = None
            return False

        data = fp.read().strip().split('\n')
        self.uname = data[0]
        self.passwd = data[1]

        LOG(msg='Credentials have been set. Username:%s - Password:%s' %(self.uname, self.passwd), log=Logs.INFO)
        return True

    def get_username(self):
        return self.uname

    def get_password(self):
        return self.passwd

    def set_username(self, username):
        self.uname = username

    def set_password(self, password):
        self.passwd = password

    def check_credential(self):
        return self.uname and self.passwd