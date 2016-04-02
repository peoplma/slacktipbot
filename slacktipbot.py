import time
import json
import re
import traceback
from slacksocket import SlackSocket
from slackclient import SlackClient
from block_io import BlockIo
version = 2 # API version
from blockio_key_pin1 import *
block_io_doge = BlockIo(blockio_api_doge_key, blockio_secret_pin, version) 
block_io_btc = BlockIo(blockio_api_btc_key, blockio_secret_pin, version)
block_io_ltc = BlockIo(blockio_api_ltc_key, blockio_secret_pin, version)
ss = SlackSocket(slack_token,translate=False) # translate will lookup and replace user and channel IDs with their human-readable names. default true. 
sc = SlackClient(slack_token)

def main():
	time.sleep(1)
	for event in ss.events():
		j = json.loads(event.json)
		print(j['type'])
		if j['type'] != 'message':
			continue

		if 'tipbot kill all humans' in str(j['text']):
			print(sc.api_call("chat.postMessage", channel="#general", text='http://i.imgur.com/nwLy8Rd.jpg', username='pybot', icon_emoji=':robot_face:'))
			continue


		if '!tipbot' not in j['text']:
			continue

		# user name/id lookups
		id2name = {}
		name2id = {}
		try:
			users = sc.api_call("users.list")
			for user in users['members']:
				id2name[user['id']] = user['name']
				name2id[user['name']] = user['id']
		except:
			print('failed to build user lookups')
			continue

		# split message and find '!tipbot'
		splitmessage = j['text'].split()
		print(splitmessage)
		tipindex = 0
		for i in range(0, len(splitmessage), 1):
			if splitmessage[i] is '!tipbot':
				tipindex = i
				break

		# !tipbot tip
		if splitmessage[tipindex + 1] is 'tip':
			if not isfloat(splitmessage[tipindex + 2]):
				print('amount not float ='+splitmessage[tipindex + 2])
				continue
			amount = float(splitmessage[tipindex + 2])
			if amount < 0:
				print('negative amount ='+splitmessage[tipindex + 2])
				continue

			coin = splitmessage[tipindex + 3]

			# get list of valid users from command
			users = []
			for i in range(4, len(splitmessage), 1):
				if splitmessage[i] in name2id.keys():
					users.append(splitmessage[i]);

			# build api strings
			tousers = str(','.join(name2id[user] for user in users))
			toreadable = str(','.join(users))
			toeach = str(','.join(str(amount) for user in users))

			print(id2name[j['user']]+' ('+j['user']+') tipped '+str(amount)+' '+coin+' to '+toreadable+' ('+tousers+')')

			if coin is 'doge':
				try:
					block_io_doge.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to tip doge')
					continue
			elif coin is 'ltc':
				try:
					block_io_ltc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to tip ltc')
					continue
			elif coin is 'btc':
				try:
					block_io_btc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to tip btc')
					continue

		# !tipbot make it rain
		elif splitmessage[tipindex + 1] is 'make':
			if splitmessage[tipindex + 2] is not 'it' or splitmessage[tipindex + 3] is not 'rain':
				continue

			if not isfloat(splitmessage[tipindex + 4]):
				print('amount not float ='+splitmessage[tipindex + 4])
				continue
			amount = float(splitmessage[tipindex + 4])
			if amount < 0:
				print('negative tip ='+splitmessage[tipindex + 4])
				continue

			coin = splitmessage[tipindex + 5]

			if coin is 'doge':
				try:
					addresses = block_io_doge.get_my_addresses()
					amounteach = amount / (len(addresses['data']['addresses']) - 2)
					# amount / (number of addresses - current user & default)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toreadable = str(','.join(id2name[addr['label']] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_doge.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain doge')
					continue
			elif coin is 'ltc':
				try:
					addresses = block_io_ltc.get_my_addresses()
					amounteach = amount / (len(addresses['data']['addresses']) - 2)
					# amount / (number of addresses - current user & default)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toreadable = str(','.join(id2name[addr['label']] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_ltc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain ltc')
					continue
			elif coin is 'btc':
				try:
					addresses = block_io_btc.get_my_addresses()
					amounteach = amount / (len(addresses['data']['addresses']) - 2)
					# amount / (number of addresses - current user & default)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toreadable = str(','.join(id2name[addr['label']] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_btc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain btc')
					continue

		# !tipbot withdraw
		elif splitmessage[tipindex + 1] is 'withdraw':
			amount = splitmessage[tipindex + 2]
			coin = splitmessage[tipindex + 3]
			address = splitmessage[tipindex + 4]

			print(id2name[j['user']]+' ('+j['user']+') withdraws '+amount+' '+coin+' to '+address)

			if coin is 'doge':
				try:
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to withdraw doge')
					continue
			elif coin is 'ltc':
				try:
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to withdraw ltc')
					continue
			elif coin is 'btc':
				try:
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
					print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to withdraw btc')
					continue

		# !tipbot addresses
		elif splitmessage[tipindex + 1] is 'addresses':
			coin = splitmessage[tipindex + 2]

			if coin is 'doge':
				try:
					addresses = block_io_doge.get_my_addresses()
					for address in addresses['data']['addresses']:
						balance = block_io_doge.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					print('failed to get doge addresses')
					continue
			elif coin is 'ltc':
				try:
					addresses = block_io_ltc.get_my_addresses()
					for address in addresses['data']['addresses']:
						balance = block_io_ltc.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					print('failed to get ltc addresses')
					continue
			elif coin is 'btc':
				try:
					addresses = block_io_btc.get_my_addresses()
					for address in addresses['data']['addresses']:
						balance = block_io_btc.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					print('failed to get btc addresses')
					continue

		# !tipbot register
		elif splitmessage[tipindex + 1] is 'register':
			try:
				block_io_doge.get_new_address(label=j['user'])
			except:
				print('failed to create doge address for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				block_io_ltc.get_new_address(label=j['user'])
			except:
				print('failed to create ltc address for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				block_io_btc.get_new_address(label=j['user'])
			except:
				print('failed to create btc address for '+id2name[j['user']]+' ('+j['user']+')')

			print(sc.api_call("chat.postMessage", channel="#general", text=id2name[j['user']].' registered!  :tada:', username='pybot', icon_emoji=':robot_face:'))

		# !tipbot check
		elif splitmessage[tipindex + 1] is 'check':
			try:
				balance = block_io_doge.get_address_balance(labels=j['user'])
				address = block_io_doge.get_address_by_label(label=j['user'])
				print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s doge' % (id2name[j['user']]+' dogecoin: ', address['data']['address'], balance['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
			except:
				print('failed to check doge for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				balance = block_io_ltc.get_address_balance(labels=j['user'])
				address = block_io_ltc.get_address_by_label(label=j['user'])
				print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s ltc' % (id2name[j['user']]+' litecoin: ', address['data']['address'], balance['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
			except:
				print('failed to check ltc for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				balance = block_io_btc.get_address_balance(labels=j['user'])
				address = block_io_btc.get_address_by_label(label=j['user'])
				print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s btc' % (id2name[j['user']]+' bitcoin: ', address['data']['address'], balance['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
			except:
				print('failed to check btc for '+id2name[j['user']]+' ('+j['user']+')')

		# !tipbot help
		elif splitmessage[tipindex + 1] is 'help':
			print(sc.api_call("chat.postMessage", channel="#general", text='https://github.com/peoplma/slacktipbot', username='pybot', icon_emoji=':robot_face:'))


def secondary():
	try:
		while True:
			main()
	except:
		traceback.print_exc()
		print('Resuming in 2sec...')
		time.sleep(2)
		print('Resumed')
while True:
	secondary()
