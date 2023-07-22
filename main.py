
import os
import json
import datetime
import os.path
import time
import requests

interV = 15  # Script repeat interval in seconds
looper = False  # variable for deciding looping mechanism
bot_token = "5866208034:AAE9685WjS-3Cx48fahACoXLCLT0dj7Ro6Y"
chat_id = "5227929164"

print("Welcome to SMS Forwarder v:1.1")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# New function to send SMS to Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()

# Updated function for forwarding SMS
def smsforward(looping=False):
    global looper  # referencing main looper variable

    lastSMS = datetime.datetime.now()
    tmpFile = "tmpLastTime.txt"
    cfgFile = "config.txt"

    # Checking existence of configuration file
    if not os.path.exists(cfgFile):
        # file not found. creating a new configuration file
        cfile = open(cfgFile, "a")
        filters = input(f"{bcolors.BOLD}Please enter keyword filter(s) separated by comma (',') : {bcolors.ENDC}")
        filter_s = filters.split(",")
        cfile.write(filters.lower())
        cfile.write("\n")
        print("")
        print("")
        cfile.close()
    else:
        # configuration file is already there. reading configurations
        rst = "1"
        if not looping:
            print(f"""{bcolors.BOLD}Old configuration file found! What do You want to do?{bcolors.ENDC}
                {bcolors.OKGREEN}1) Continue with old settings{bcolors.ENDC}
                {bcolors.WARNING}2) Remove old settings and start afresh{bcolors.ENDC}""")
            rst = input("Please enter your choice number: ")
        if rst == "1":
            print(f"{bcolors.OKGREEN}Starting with old settings...........{bcolors.ENDC}")
            cfile = open(cfgFile, "r")
            cdata = cfile.read().splitlines()
            filter_s = cdata[0].split(",")
        elif rst == "2":
            print(f"{bcolors.WARNING}Removing old Configuration files..........{bcolors.ENDC}")
            os.remove(cfgFile)
            os.remove(tmpFile)
            print(f"{bcolors.WARNING}Old configuration files removed. Please enter new settings{bcolors.ENDC}")
            smsforward()

    # Chcking last saved forward time
    if not os.path.exists(tmpFile):
        # Saved time time not found. Setting up and saving current time as last forward time
        print("Last time not found. Setting it to current Date-Time")
        tfile = open(tmpFile, "w")
        tfile.write(str(lastSMS))
        tfile.close()
    else:
        # Saved last sms forward time found. loading from that
        tfile = open(tmpFile, "r")
        lastSMS = datetime.datetime.fromisoformat(tfile.read())
        tfile.close()

    if not looper:
        # ask user to run the script on repeat
        lop = input(f"Keep running after each {interV} second (y/n): ")
        if lop == "y":
            looper = True  # This will keep the script running after the defined interval
            print("You can stop the script anytime by pressing Ctrl+C")
    print(f"Last SMS forwarded on {lastSMS}")
    jdata = os.popen("termux-sms-list -l 50").read()  # Reading latest 50 SMSs using termux-api
    try:
        jd = json.loads(jdata)  # storing JSON output
    except json.JSONDecodeError as e:
        print(f"{bcolors.FAIL}Error decoding JSON: {e}{bcolors.ENDC}")
        print(f"{bcolors.FAIL}JSON Data: {jdata}{bcolors.ENDC}")
        return
    print(f"Reading {len(jd)} latest SMSs")

    for j in jd:
        if datetime.datetime.fromisoformat(j['received']) > lastSMS:  # Comparing SMS timing
            for f in filter_s:
                if f in j['body'].lower() and j['type'] == "inbox":  # Checking if the SMS is in inbox and the filter(s) are matching
                    print(f"{f} found")
                    # Sending the forwarded SMS to Telegram
                    message = f"SMS Forwarded:\nFrom: {j['address']}\nBody: {j['body']}"
                    print("Sending to Telegram:", message)
                    send_to_telegram(message)

                    tfile = open(tmpFile, "w")
                    tfile.write(j['received'])
                    tfile.close()

# calling sms forward function for the first time
smsforward()

# if the user decided to repeat the script execution, the following loop will do that
while looper:
    time.sleep(interV)
    smsforward(looping=True)
    
