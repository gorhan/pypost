from pypost.mail_server import mail_server
from pypost.log import LOG, Logs

credential_file = './credential.txt'

def get_parameters_manually(server):
    try:
        if not server.set_credentials_from_file(credential_file):
            inp = raw_input('Are you using credential file? [Y/n]: ')
            if inp == '' or inp.capitalize() == 'Y':
                file_path = raw_input('Enter a credential file: ')

                while True:
                    if server.set_credentials_from_file(file_path):
                        break
                    file_path = raw_input('Enter a valid credential file: ')
            else:
                server.set_credentials_from_stdin()

        if not server.connect():
            return False

        from_addr = raw_input('FROM: ')
        if not server.set_from(from_addr):
            return False

        while True:
            to_addr = raw_input('TO: ')
            if not server.add_to(to_addr):
                break

        subject = raw_input('SUBJECT: ')
        msg = raw_input('MESSAGE:\n') + '\n'
        new_line_counter = 0
        while True:
            row = raw_input()
            if row == '':
                new_line_counter += 1
                if new_line_counter >= 2:
                    break
                else:
                    msg += row + '\n'
            else:
                msg += row + '\n'
                new_line_counter = 0

        server.set_message(subject, msg)

        inp = raw_input('Do you want to add image? [Y/n]: ')
        while True:
            if inp == '' or inp.capitalize() == 'Y':
                file_path = raw_input('Enter an image file: ')

                while True:
                    if server.add_image_file(file_path):
                        break
                    file_path = raw_input('Enter a valid image file: ')
            else:
                break

            inp = raw_input('Do you want to add another image? [y/N]: ')
            inp = 'N' if inp == '' or inp.capitalize() == 'N' else inp.capitalize()

        return True
    except KeyboardInterrupt:
        LOG(msg='SIGINT signal is caught...', log=Logs.WARN)
        server.disconnect()
        return False

if __name__ == '__main__':
    mail_server = mail_server()
    if get_parameters_manually(mail_server):
        mail_server.send_message()
        mail_server.disconnect()
