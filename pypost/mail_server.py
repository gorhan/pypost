import stmplib
import re
from log import LOG, Logs
from credential import credential

GMAIL_SMTP_SERVER_ADDR = 'smtp.gmail.com:587'
MAIL_PATTERN = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


class mail_server(credential):
    def __init__(self, username=None, password=None):
        credential.__init__(username, password)

        self.server_addr = GMAIL_SMTP_SERVER_ADDR
        self.smtp_server = None

        self.sender_addr = None
        self.receiver_addrs = list()

        self.subject = None
        self.message = None

    def set_server_address(self, server_address):
        self.server_addr = server_address

    def get_server_address(self):
        return self.server_addr

    def set_from(self, mail_address):
        if re.match(MAIL_PATTERN, mail_address):
            self.sender_addr = mail_address
            LOG(msg='Sender mail address: %s' % self.sender_addr, log=Logs.INFO)
            return True

        LOG(msg='Invalid mail address: %s' % mail_address, log=Logs.ERROR)
        return False

    def add_to(self, mail_address):
        if re.match(MAIL_PATTERN, mail_address):
            if mail_address not in self.receiver_addrs:
                self.receiver_addrs.append(mail_address)
                LOG(msg='Receiver mail address is added: %s' % self.receiver_addrs[-1], log=Logs.INFO)
            else:
                LOG(msg='Receiver mail address is already in the list: %s' % mail_address, log=Logs.WARN)

            return True

        LOG(msg='Invalid mail address: %s' % mail_address, log=Logs.ERROR)
        return False

    def get_from(self):
        return self.receiver_addrs

    def set_message(self, subject, text):
        self.subject = subject
        self.message = text

    def connect(self):
        try:
            self.smtp_server = smtplib.SMTP(self.server_addr)
            self.smtp_server.starttls()
            self.smtp_server.login(self.uname, self.passwd)
        except gaierror:
            LOG(msg='Unable to connect to SMTP mail server: %s' % (self.server_addr if self.server_addr else 'None'), log=Logs.ERROR)
            return False

        LOG(msg='Connection to the SMTP server is established.', log=Logs.INFO)
        return True

    def send_message(self):
        if self.check_all():
            email = '''
            FROM: %s
            TO: %s
            Subject: %s

            %s
            ''' % (self.sender_addr, ', '.join(self.receiver_addrs), self.subject, self.message)

            self.smtp_server.sendmail(self.sender_addr, self.receiver_addrs, email)
            return True

        LOG(msg='Unexpected error occurred.', log=Logs.ERROR)
        return False

    def check_all(self):
        return self.check_credential() and \
            self.sender_addr and \
            self.receiver_addrs and \
            self.server_addr and \
            self.smtp_server and \
            self.message and \
            self.subject