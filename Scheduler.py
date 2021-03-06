import schedule
import time
import os
import datetime
from threading import Thread
from NotificationWorker import Notifier
from Apartments import Kiara, Stratus, McKenzie, Cirrus


APARTMENTS = [Kiara(), Stratus(), McKenzie(), Cirrus()]

CONTACTS  = [{"number":os.environ["MY_NUMBER"], "carrier":"vzw"}]



def check_reservations(debug=False):
    print("Started at {}".format(datetime.datetime.now()))
    messenger = Notifier()
    for a in APARTMENTS:
        print("Checking {}".format(type(a).__name__))
        try:
            msg = a.new_listings()
            if msg is not None:
                print(msg)
            if msg is not None and not debug:
                for c in CONTACTS:
                    messenger.sendText(c["number"], c["carrier"], msg)
        except Exception as e:
            error_msg = "{} failed with error: {}".format(type(a).__name__, e)
            for c in CONTACTS:
                messenger.sendText(c["number"], c["carrier"], error_msg)
            continue




def main():
    schedule.every().hour.do(check_reservations)
    print("Schedule Set")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    check_reservations(True)
    main()
