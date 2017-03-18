import json
import traceback
import requests
from block_io import BlockIo
from slackclient import SlackClient

from define import *
from key_pin import *

version = 2  # API version


class Bot:
    def __init__(self, j):
        self.sc = SlackClient(slack_token)
        self.j = j
        self.block_io = {
            "doge": BlockIo(blockio_api_doge_key, blockio_secret_pin, version),
            "btc": BlockIo(blockio_api_btc_key, blockio_secret_pin, version),
            "ltc": BlockIo(blockio_api_ltc_key, blockio_secret_pin, version)
        }

        self.id2name = {}
        self.name2id = {}
        self.split_message = None
        self.tip_index = 0

    def get_command(self):
        # split message and find '!tipbot'
        self.split_message = self.j['text'].split()
        print(self.split_message)
        for i in range(0, len(self.split_message), 1):
            if self.split_message[i] == '!tipbot':
                self.tip_index = i
                break
        try:
            return self.split_message[self.tip_index + 1]
        except:
            pass

    def update_user(self):
        # user name/id lookups
        try:
            users = self.sc.api_call("users.list")
            for user in users['members']:
                self.id2name[user['id']] = user['name']
                self.name2id[user['name']] = user['id']
        except:
            print('failed to build user lookups')
            pass

    def send_message(self, chan, message, username='pybot', icon=':robot_face:'):
        return self.sc.api_call("chat.postMessage", channel=chan, text=message, username=username, icon_emoji=icon)

    def help(self):
        print(self.send_message(self.j['channel'], 'https://github.com/peoplma/slacktipbot-origin'))

    def get_coin_value(coin, balance):
        try:
            c_currency = requests.get(coincap[coin])
            jc_currency = c_currency.json()
            print(coin + ' $' + str(jc_currency['usdPrice']))
            usd_currency = float(
                "{0:.2f}".format(float(balance['data']['available_balance']) * float(jc_currency['usdPrice'])))
            return usd_currency
        except:
            try:
                c_currency = requests.get(cryptocompare[coin])
                jc_currency = c_currency.json()
                print(coin + ' $' + str(jc_currency['Data'][0]['Price']))
                usd_currency = float(
                    "{0:.2f}".format(
                        float(balance['data']['available_balance']) * float(jc_currency['Data'][0]['Price'])))
                return usd_currency
            except:
                traceback.print_exc()

    def check(self):
        for currency_name, currency in self.block_io.items():
            try:
                balance = currency.get_address_balance(labels=self.j['user'])
                address = currency.get_address_by_label(label=self.j['user'])

                usd_currency = self.get_coin_value(currency_name, balance)
                print(usd_currency)
                message = self.id2name[self.j['user']] + currency_name \
                          + ': - ' \
                          + address['data']['address'] + ' - ' \
                          + balance['data']['available_balance'] \
                          + currency_name + ' ~$' \
                          + str(usd_currency)
                print(self.send_message(self.j['channel'], message))
            except:
                traceback.print_exc()
                print('failed to check ' + currency_name + ' for ' + self.id2name[self.j['user']] + ' (' + self.j[
                    'user'] + ')')

    def register(self):
        for currency_name, currency in self.block_io.items():
            try:
                currency.get_new_address(label=self.j['user'])
            except:
                traceback.print_exc()
                print(
                    'failed to create ' + currency_name + ' address for ' + self.id2name[self.j['user']] + ' (' +
                    self.j[
                        'user'] + ')')

        print(
            self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' registered!  :tada:'))

    def addresses(self):
        if len(self.split_message) < (self.tip_index + 2):
            return

        coin = self.split_message[self.tip_index + 2]
        if coin not in min_amount.keys():
            print('unknown coin =' + coin)
            return

        for currency_name, currency in self.block_io.items():
            if coin == currency_name:
                try:
                    addresses = currency.get_my_addresses()
                    for address in addresses['data']['addresses']:
                        if address['label'] not in self.id2name.keys():
                            continue
                        balance = currency.get_address_balance(addresses=address['address'])
                        message = '|' + self.id2name[address['label']] \
                                  + '|-- :  ' + address['address'] + ': ' \
                                  + balance['data']['available_balance']
                        print(self.send_message(self.j['channel'], message))

                except:
                    traceback.print_exc()
                    print('failed to get ' + currency_name + ' addresses')
                    return

    def tip(self):
        if len(self.split_message) < (self.tip_index + 4):
            return
        coin = self.split_message[self.tip_index + 3]
        if coin not in min_amount.keys():
            print('unknown coin =' + coin)
            return

        if self.split_message[self.tip_index + 2] != 'all':
            try:
                amount = float(self.split_message[self.tip_index + 2])
            except:
                print('amount not float =' + self.split_message[self.tip_index + 2])
                return
            if amount < min_amount[coin]:
                print('amount too low =' + self.split_message[self.tip_index + 2])
                print(self.send_message(self.j['channel'],
                                        'Sorry ' + self.id2name[self.j['user']] + ', you need to tip at least ' +
                                        min_amount[coin] + ' ' + coin))
                return

        # get list of valid users from command
        users = []
        accounts = self.block_io[coin].get_my_addresses()
        reg_users = []
        for g in range(0, len(accounts['data']['addresses']), 1):
            try:
                reg_users.append(accounts['data']['addresses'][g]['label'])
            except:
                continue
        for i in range(self.tip_index + 4, len(self.split_message), 1):
            if self.split_message[i] in self.name2id.keys():
                users.append(self.split_message[i]);
            if self.name2id[self.split_message[i]] not in reg_users:
                print(self.send_message(self.j['channel'],
                                        self.split_message[i] + ' is not registered.  Please !tipbot register '))

        # build api strings
        to_users = str(','.join(self.name2id[user] for user in users))
        to_readable = str(','.join(users))
        if self.split_message[self.tip_index + 2] != 'all':
            to_each = str(','.join(str(amount) for user in users))
            print(self.id2name[self.j['user']] + ' (' + self.j['user'] + ') tipped ' + str(
                amount) + ' ' + coin + ' to ' + to_readable + ' (' + to_users + ')')

        if self.split_message[self.tip_index + 2] == 'all':
            try:
                balance_currency = self.block_io[coin].get_address_balance(labels=self.j['user'])
                print(balance_currency['data']['available_balance'])
                fee = self.block_io[coin].get_network_fee_estimate(
                    amounts=balance_currency['data']['available_balance'],
                    to_labels=to_users, priority='low')
                print(fee)
                balance_minus_fee = float(balance_currency['data']['available_balance']) - float(
                    fee['data']['estimated_network_fee'])
                print(balance_minus_fee)
                self.block_io[coin].withdraw_from_labels(amounts=balance_minus_fee, from_labels=self.j['user'],
                                                         to_labels=to_users, priority='low')
                print(self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' tipped ' + str(
                    balance_minus_fee) + ' ' + coin + ' to ' + to_readable + '!  :+1:'))
            except:
                try:
                    exc = traceback.format_exc()
                    splitexc = exc.split()
                    n = len(splitexc) - 2
                    print(splitexc[n])
                    self.block_io[coin].withdraw_from_labels(amounts=splitexc[n], from_labels=self.j['user'],
                                                             to_labels=to_users, priority='low')
                    print(self.send_message(self.j['channel'],
                                            self.id2name[self.j['user']] + ' tipped ' + str(
                                                splitexc[n]) + ' ' + coin + ' to ' + to_readable + '!  :+1:'))
                except:
                    traceback.print_exc()
                    print('failed to tip all ' + coin)
                    return
        else:
            try:
                self.block_io[coin].withdraw_from_labels(amounts=to_each, from_labels=self.j['user'],
                                                         to_labels=to_users,
                                                         priority='low')
                print(self.send_message(self.j['channel'],
                                        self.id2name[self.j['user']] + ' tipped ' + to_readable + ' ' + str(
                                            amount) + ' ' + coin + '!  :moon:'
                                        ))
            except:
                try:
                    exc = traceback.format_exc()
                    splitexc = exc.split()
                    n = len(splitexc) - 2
                    print(splitexc[n])
                    self.block_io[coin].withdraw_from_labels(amounts=splitexc[n], from_labels=self.j['user'],
                                                             to_labels=to_users, priority='low')
                    print(self.send_message(self.j['channel'],
                                            self.id2name[self.j['user']] + ' tipped ' + str(
                                                splitexc[n]) + ' ' + coin + ' to ' + to_readable + '!  :+1:'))
                except:
                    traceback.print_exc()
                    print('failed to tip all ' + coin)
                    return

    def make(self):
        if len(self.split_message) < (self.tip_index + 5):
            return
        if self.split_message[self.tip_index + 2] != 'it' or self.split_message[self.tip_index + 3] != 'rain':
            return

        coin = self.split_message[self.tip_index + 5]
        if coin not in min_amount.keys():
            print('unknown coin =' + coin)
            return

        try:
            amount = float(self.split_message[self.tip_index + 4])
        except:
            print('amount not float =' + self.split_message[self.tip_index + 4])
            return
        if amount < min_amount[coin]:
            print('amount too low =' + self.split_message[self.tip_index + 4])
            print(self.send_message(self.j['channel'],
                                    'Sorry ' + self.id2name[self.j['user']] + ', you need to tip at least ' +
                                    min_amount[coin] + ' ' + coin))
            return

        try:
            addresses = self.block_io[coin].get_my_addresses()
            users = []
            for user in addresses['data']['addresses']:
                if user['label'] in self.id2name.keys() and user['label'] != self.j['user']:
                    users.append(user['label'])
            if len(self.split_message) > 6 and self.split_message[self.tip_index + 6] == 'online':
                try:
                    user_on_list = self.sc.api_call("users.list", presence='1')
                    for o in range(0, 99, 1):
                        try:
                            if user_on_list['members'][o]['presence'] == 'away':
                                try:
                                    users.remove(user_on_list['members'][o]['id'])
                                except:
                                    continue
                        except:
                            continue
                except:
                    return
            amount_each = amount / len(users)
            if amount_each < min_amount[coin]:
                print('amounteach too small =' + amount_each)
                print(self.send_message(self.j['channel'],
                                        'Sorry ' + self.id2name[self.j['user']] + ', you need to tip at least ' +
                                        min_amount[coin] + ' ' + coin))
                return
            to_users = str(','.join(user for user in users))
            to_readable = str(','.join(self.id2name[user] for user in users))
            to_each = str(','.join('%.8f' % amount_each for user in users))
            print(self.id2name[self.j['user']] + ' (' + self.j[
                'user'] + ') made it rain on ' + to_readable + ' (' + to_users + ') ' + str(
                amount) + ' (' + '%.8f' % amount_each + ' each)');
            self.block_io[coin].withdraw_from_labels(amounts=to_each, from_labels=self.j['user'], to_labels=to_users,
                                                     priority='low')
            print(self.send_message(self.j['channel'], self.id2name[self.j[
                'user']] + ' tipped  ' + to_readable + ' ' + '%.8f' % amount_each + ' ' + coin + '!  :moon:'))
        except:
            traceback.print_exc()
            print('failed to make it rain ' + coin)
            return

    def withdraw(self):
        if len(self.split_message) < (self.tip_index + 4):
            return

        amount = self.split_message[self.tip_index + 2]
        coin = self.split_message[self.tip_index + 3]
        address = self.split_message[self.tip_index + 4]

        if coin not in min_amount.keys():
            print('unknown coin =' + coin)
            return

        print(
            self.id2name[self.j['user']] + ' (' + self.j[
                'user'] + ') withdraws ' + amount + ' ' + coin + ' to ' + address)

        if amount == 'all':
            try:
                balance_currency = self.block_io[coin].get_address_balance(labels=self.j['user'])
                print(balance_currency['data']['available_balance'])
                fee = self.block_io[coin].get_network_fee_estimate(
                    amounts=balance_currency['data']['available_balance'],
                    to_addresses=address, priority='low')
                print(fee)
                balance_minus_fee = float(balance_currency['data']['available_balance']) - float(
                    fee['data']['estimated_network_fee'])
                print(balance_minus_fee)
                self.block_io[coin].withdraw_from_labels(amounts=balance_minus_fee, from_labels=self.j['user'],
                                                         to_addresses=address, priority='low')
                print(self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' withdrew ' + str(
                    amount) + ' ' + coin + ' to ' + address + '!  :+1:'
                                        ))
            except:
                try:
                    exc = traceback.format_exc()
                    splitexc = exc.split()
                    n = len(splitexc) - 2
                    print(splitexc[n])
                    self.block_io[coin].withdraw_from_labels(amounts=splitexc[n], from_labels=self.j['user'],
                                                             to_addresses=address, priority='low')
                    print(self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' withdrew ' + str(
                        amount) + ' ' + coin + ' to ' + address + '!  :+1:'
                                            ))
                except:
                    traceback.print_exc()
                    print('failed to withdraw ' + coin)
                    return
        else:
            try:
                self.block_io[coin].withdraw_from_labels(amounts=amount, from_labels=self.j['user'],
                                                         to_addresses=address,
                                                         priority='low')
                print(self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' withdrew ' + str(
                    amount) + ' ' + coin + ' to ' + address + '!  :+1:'
                                        ))
            except:
                try:
                    exc = traceback.format_exc()
                    splitexc = exc.split()
                    n = len(splitexc) - 2
                    print(splitexc[n])
                    self.block_io[coin].withdraw_from_labels(amounts=splitexc[n], from_labels=self.j['user'],
                                                             to_addresses=address, priority='low')
                    print(self.send_message(self.j['channel'], self.id2name[self.j['user']] + ' withdrew ' + str(
                        splitexc[n]) + ' ' + coin + ' to ' + address + '!  :+1:'))
                except:
                    traceback.print_exc()
                    print('failed to withdraw ' + coin)
                    return

    def shift(self):
        if len(self.split_message) < (self.tip_index + 3):
            return

        amount = self.split_message[self.tip_index + 2]
        coin = self.split_message[self.tip_index + 3]
        pairs = set(['btc_ltc', 'btc_doge', 'ltc_btc', 'ltc_doge', 'doge_btc', 'doge_ltc'])
        if coin not in pairs:
            print('unknown coin =' + coin)
            return

        print(self.id2name[self.j['user']] + ' (' + self.j['user'] + ') shifted ' + amount + ' ' + coin)

        coin_shift = coin.split('_')
        if coin == 'btc_ltc':
            try:
                address_from = self.block_io[coin_shift[0]].get_address_by_label(label=self.j['user'])
                address_to = self.block_io[coin_shift[1]].get_address_by_label(label=self.j['user'])
                payload = {"withdrawal": address_to['data']['address'], "pair": "btc_ltc",
                           "returnAddress": address_from['data']['address'], "apiKey": shapeshift_pubkey}
                print(payload)
                try:
                    r = requests.post(url, data=payload)
                    j_response = r.json()
                    print(j_response)
                except:
                    traceback.print_exc()
                    print('failed generate shapeshift transaction')
                    return
                amount = float(
                    ''.join(ele for ele in self.split_message[self.tip_index + 2] if ele.isdigit() or ele == '.'))
                print(amount)
                self.block_io['btc'].withdraw_from_labels(amounts=amount, from_labels=self.j['user'],
                                                          to_addresses=j_response['deposit'], priority='low')
                message = str(self.id2name[self.j['user']]) \
                          + ' shifted ' + str(amount) \
                          + coin_shift[0] + ' to ' \
                          + coin_shift[1] + '!  :unicorn_face:'
                print(self.send_message(self.j['channel'], message))
            except:
                try:
                    exc = traceback.format_exc()
                    split_exc = exc.split()
                    n = len(split_exc) - 2
                    print(split_exc[n])
                    self.block_io['btc'].withdraw_from_labels(amounts=split_exc[n], from_labels=self.j['user'],
                                                              to_addresses=j_response['deposit'], priority='low')
                    print(self.send_message(self.j['channel'], str(self.id2name[self.j['user']]) + ' shifted ' + str(
                        split_exc[n]) + coin_shift[0] + ' to ' + coin_shift[
                                                1] + ' :unicorn_face:'
                                            ))
                except:
                    traceback.print_exc()
                    print('failed to shift' + coin_shift[0] + ' to ' + coin_shift[1])
                    return
