# coding: utf-8

import smtplib

from email.mime.text import MIMEText


class Sender(object):
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_pass):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def send(self, title, mail_from, mail_to, body):
        msg = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
        msg['Subject'] = title
        msg['From'] = mail_from
        msg['To'] = mail_to

        connection = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        connection.login(self.smtp_user, self.smtp_pass)
        connection.sendmail(self.smtp_user, mail_to, msg.as_string())
