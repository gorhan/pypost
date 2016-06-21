import smtplib
import re
from log import LOG, Logs
from os.path import isfile, basename
from credential import credential
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

GMAIL_SMTP_SERVER_ADDR = 'smtp.gmail.com:587'
MAIL_PATTERN = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


class mail_server(credential):
    def __init__(self, username=None, password=None):
        credential.__init__(self, username, password)

        self.server_addr = GMAIL_SMTP_SERVER_ADDR
        self.smtp_server = None

        self.sender_addr = None
        self.receiver_addrs = list()

        self.subject = None
        self.message = None
        self.image_files = list()

    def set_server_address(self, server_address):
        self.server_addr = server_address

    def get_server_address(self):
        return self.server_addr

    def set_from(self, mail_address_alias):
        mail_address = mail_address_alias.split(',')
        alias = mail_address[0].strip()
        mail_address = mail_address[-1].strip()
        if re.match(MAIL_PATTERN, mail_address):
            if alias is None:
                alias = mail_address

            self.sender_addr = (alias, mail_address)
            LOG(msg='Sender mail address: %s <%s>' % (self.sender_addr[0], self.sender_addr[1]), log=Logs.INFO)
            return True

        LOG(msg='Invalid mail address: %s' % mail_address, log=Logs.ERROR)
        return False

    def add_to(self, mail_address_alias):
        mail_address = mail_address_alias.split(',')
        alias = mail_address[0].strip()
        mail_address = mail_address[-1].strip()
        if re.match(MAIL_PATTERN, mail_address):
            if alias is None:
                alias = mail_address

            if (alias, mail_address) not in self.receiver_addrs:
                self.receiver_addrs.append((alias, mail_address))
                LOG(msg='Receiver mail address is added: %s <%s>' % (self.receiver_addrs[-1][0], self.receiver_addrs[-1][1]), log=Logs.INFO)
            else:
                LOG(msg='Receiver mail address is already in the list: %s' % mail_address, log=Logs.WARN)

            return True

        LOG(msg='Invalid mail address: %s' % mail_address, log=Logs.ERROR)
        return False

    def in_receiver_list(self, mail_addr):
        for index, receiver in self.receiver_addrs:
            if mail_addr in receiver:
                return index
        return -1

    def remove_receiver(self, mail_addr):
        index = self.in_receiver_list(mail_addr)
        if index != -1:
            removed_receiver = self.receiver_addrs.pop(index)
            LOG(msg='%s <%s> is removed from the recipients list' % (removed_receiver[0], removed_receiver[1]), log=Logs.INFO)
            return True

        LOG(msg='%s is not in the recipients list' % mail_addr, log=Logs.INFO)
        return False

    def clear_receivers(self):
        self.receiver_addrs = list()
        LOG(msg='All recipients are removed...', log=Logs.INFO)

    def get_sender(self):
        return self.sender_addr

    def get_receivers(self):
        return self.receiver_addrs

    def set_message(self, subject, text):
        self.subject = subject
        self.message = text

    def add_image_file(self, file_name):
        if not isfile(file_name):
            LOG(msg='The file does not exist: Filename: %s' % file_name, log=Logs.INFO)
            return False
        elif file_name in self.image_files:
            LOG(msg='The file is already in the list', log=Logs.INFO)
            return False

        self.image_files.append(file_name)
        LOG(msg='The image file is added', log=Logs.INFO)
        return True

    def connect(self):
        try:
            self.smtp_server = smtplib.SMTP(self.server_addr)
            self.smtp_server.starttls()
            self.smtp_server.login(self.uname, self.passwd)
        except Exception as e:
            LOG(msg='Unable to connect to SMTP mail server: %s: %s' % (self.server_addr if self.server_addr else 'None', e.message), log=Logs.ERROR)
            return False

        LOG(msg='Connection to the SMTP server is established.', log=Logs.INFO)
        return True

    def __package_mail(self):
        if not self.check_all():
            return None

        mail = MIMEMultipart()
        mail['SUBJECT'] = self.subject
        mail['FROM'] = '%s <%s>' % (self.sender_addr[0], self.sender_addr[1])
        mail['TO'] = ','.join('%s <%s>' % (alias, mail_addr) for alias, mail_addr in self.receiver_addrs)

        text = MIMEText(self.message, 'plain')
        html = MIMEText('<p><b>-- The message contains %d characters! --</b></p>' % len(self.message), 'html')

        mail.attach(text)

        for image_file in self.image_files:
            fp = open(image_file, 'rb')
            image = fp.read()
            attachment = MIMEImage(image, name=basename(image_file))
            mail.attach(attachment)

        mail.attach(html)

        return mail

    def send_message(self):
        mail = self.__package_mail()

        if mail:
            self.smtp_server.sendmail(self.sender_addr[1], [receiver_addr for _, receiver_addr in self.receiver_addrs], mail.as_string())
            LOG(msg='Your mail has been sent successfully...', log=Logs.INFO)
            return True

        LOG(msg='Unexpected error occurred.', log=Logs.ERROR)
        return False

    def disconnect(self):
        self.smtp_server.close()
        LOG(msg='SMTP Server is disconnected...', log=Logs.INFO)
        return True

    def check_all(self):
        return self.check_credential() and \
            self.sender_addr and \
            self.receiver_addrs and \
            self.server_addr and \
            self.smtp_server and \
            self.message and \
            self.subject