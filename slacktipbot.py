import time
import json
import re
import traceback
import requests
import threading

from slacksocket import SlackSocket

import botCommand

from key_pin import *

ss = SlackSocket(slack_token, translate=False)  # translate will lookup and replace user and channel IDs with their human-readable names. default true.

def main():
    time.sleep(1)
    for event in ss.events():
        j = json.loads(event.json)
        if j['type'] != 'message':
            continue

        if '!tipbot' not in j['text']:
            continue

        # print message will be parsed
        print(j['text'])

        com = botCommand.Bot(j)
        com.update_user()
        command = com.get_command()

        # !tipbot tip
        if command == 'tip':
            com.tip()

        # !tipbot make it rain
        elif command == 'make':
            com.make()

        # !tipbot withdraw
        elif command == 'withdraw':
            com.withdraw()

        # tipbot shift
        elif command == 'shift':
            com.shift()

        # !tipbot addresses
        elif command == 'addresses':
            com.addresses()

        # !tipbot register
        elif command == 'register':
            com.register()

        # !tipbot check
        elif command == 'check':
            com.check()

        # !tipbot help
        elif command == 'help':
            com.help()
