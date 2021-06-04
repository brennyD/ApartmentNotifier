# ApartmentNotifier
Text message notifier when new apartment buildings in Seattle become avaliable

Currently notifies for:
Kiara
Stratus
McKenzie
Cirrus

To run, run Scheduler.py, and sub in environment variables for GYM_SENDER_EMAIL (email that will deliver text messages), GYM_SENDER_PSWD, and MY_NUMBER

The program will check the websites every hour and text the phone number stored in MY_NUMBER (expected to be a verizon phone number)
