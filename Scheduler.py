import schedule
import time
import os
import datetime
from threading import Thread
from NotificationWorker import Notifier
from Apartments import Kiara, Stratus, McKenzie, Cirrus


APARTMENTS = [Kiara(), Stratus(), McKenzie(), Cirrus()]

CONTACTS  = [{"number":os.environ["MY_NUMBER"], "carrier":"vzw"}]



def check_reservations():
    print("Started at {}".format(datetime.datetime.now()))
    messenger = Notifier()
    for a in APARTMENTS:
        print("Checking {}".format(type(a).__name__))
        msg = a.new_listings()
        if msg is not None:
            for c in CONTACTS:
                messenger.sendText(c["number"], c["carrier"], msg)



def main():
    schedule.every().hour.do(check_reservations)
    print("Schedule Set")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    check_reservations()
    main()
