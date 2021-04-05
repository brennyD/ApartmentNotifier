import schedule
import time
import os
import datetime
from threading import Thread
from NotificationWorker import Notifier
from Apartments import Kiara, Stratus, McKenzie


APARTMENTS = [Kiara(), Stratus(), McKenzie()]

CONTACTS  = [{"number":os.environ["MY_NUMBER"], "carrier":"vzw"}]



def check_reservations():
    messenger = Notifier()
    for a in APARTMENTS:
        msg = a.new_listings()
        for c in contacts:
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
