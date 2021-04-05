import smtplib
import os
import time
from email.message import EmailMessage

SENDER_EMAIL = os.environ["GYM_SENDER_EMAIL"]
SENDER_PSWD = os.environ["GYM_SENDER_PSWD"]
EMAIL_PREFIXES = {
    "vzw": "vtext.com",
    "att": "txt.att.net",
    "sprnt": "messaging.sprintpcs.com",
    "tmbl": "tmomail.net"
    }

class Notifier:
    def __init__(self):
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(SENDER_EMAIL,SENDER_PSWD)


    def sendText(self, number, carrier, message):
        msg = EmailMessage()
        msg.set_content(message)
        msg["From"] = SENDER_EMAIL
        msg["To"] = "{}@{}".format(str(number), EMAIL_PREFIXES[carrier])
        self.server.send_message(msg)


if __name__ == "__main__":
    alerter = Notifier()
    message = "Ayo?"
    alerter.sendText(os.environ["GYM_TEST_NUMBER"], "vzw", message)
