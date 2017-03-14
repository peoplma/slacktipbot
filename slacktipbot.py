import time
import json
import re
import traceback
import requests
import threading
from slacksocket import SlackSocket
from slackclient import SlackClient
from block_io import BlockIo
version = 2 # API version
from key_pin import *
from define import *

block_io_doge = BlockIo(blockio_api_doge_key, blockio_secret_pin, version)
block_io_btc = BlockIo(blockio_api_btc_key, blockio_secret_pin, version)
block_io_ltc = BlockIo(blockio_api_ltc_key, blockio_secret_pin, version)
ss = SlackSocket(slack_token,translate=False) # translate will lookup and replace user and channel IDs with their human-readable names. default true. 
sc = SlackClient(slack_token)

def main():
	time.sleep(1)
	for event in ss.events():
		j = json.loads(event.json)
		if j['type'] != 'message':
			continue
			
		if '!tipbot' not in j['text']:
			continue

		print(j['text'])

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
			if splitmessage[i] == '!tipbot':
				tipindex = i
				break

		try:
			command = splitmessage[tipindex + 1]
		except:
			continue

		# !tipbot tip
		if command == 'tip':
			if len(splitmessage) < (tipindex + 4):
				continue
			coin = splitmessage[tipindex + 3]
			if coin not in min_amount.keys():
				print('unknown coin ='+coin)
				continue
			
			if splitmessage[tipindex + 2] != 'all':
				try:
					amount = float(splitmessage[tipindex + 2])
				except:
					print('amount not float ='+splitmessage[tipindex + 2])
					continue
				if amount < min_amount[coin]:
					print('amount too low ='+splitmessage[tipindex + 2])
					continue
					
			# get list of valid users from command
			users = []
			accounts = block_io_doge.get_my_addresses()
			reg_users = []
			for g in range(0,len(accounts['data']['addresses']),1):
				try:
					reg_users.append(accounts['data']['addresses'][g]['label'])
				except:
					continue
			for i in range(tipindex + 4, len(splitmessage), 1):
				if splitmessage[i] in name2id.keys():
					users.append(splitmessage[i]);
				if name2id[splitmessage[i]] not in reg_users:
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=splitmessage[i]+' is not registered.  Please !tipbot register ', username='pybot', icon_emoji=':robot_face:'))
				
			# build api strings
			tousers = str(','.join(name2id[user] for user in users))
			toreadable = str(','.join(users))
			if splitmessage[tipindex + 2] != 'all':
				toeach = str(','.join(str(amount) for user in users))
				print(id2name[j['user']]+' ('+j['user']+') tipped '+str(amount)+' '+coin+' to '+toreadable+' ('+tousers+')')
			
			if coin == 'doge' and splitmessage[tipindex + 2] == 'all':
				try:			
					balance_doge = block_io_doge.get_address_balance(labels=j['user'])
					print(balance_doge['data']['available_balance'])
					fee = block_io_doge.get_network_fee_estimate(amounts=balance_doge['data']['available_balance'], to_labels=tousers, priority='low')
					print(fee)
					balance_minus_fee = float(balance_doge['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_doge.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(balance_minus_fee)+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all doge')
						continue
			elif coin == 'doge':
				try:
					block_io_doge.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all doge')
						continue
			elif coin == 'ltc' and splitmessage[tipindex + 2] == 'all':
				try:			
					balance_ltc = block_io_ltc.get_address_balance(labels=j['user'])
					print(balance_ltc['data']['available_balance'])
					fee = block_io_ltc.get_network_fee_estimate(amounts=balance_ltc['data']['available_balance'], to_labels=tousers, priority='low')
					print(fee)
					balance_minus_fee = float(balance_ltc['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_ltc.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all ltc')
						continue
			elif coin == 'ltc':
				try:
					block_io_ltc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all ltc')
						continue
			elif coin == 'btc' and splitmessage[tipindex + 2] == 'all':
				try:			
					balance_btc = block_io_btc.get_address_balance(labels=j['user'])
					print(balance_btc['data']['available_balance'])
					fee = block_io_btc.get_network_fee_estimate(amounts=balance_btc['data']['available_balance'], to_labels=tousers, priority='low')
					print(fee)
					balance_minus_fee = float(balance_btc['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_btc.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped all ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_btc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all btc')
						continue		
			elif coin == 'btc':
				try:
					block_io_btc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+toreadable+' '+str(amount)+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_btc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_labels=tousers, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped '+str(splitexc[n])+' ' +coin+' to '+toreadable+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to tip all btc')
						continue

		# !tipbot make it rain
		elif command == 'make':
			if len(splitmessage) < (tipindex + 5):
				continue
			if splitmessage[tipindex + 2] != 'it' or splitmessage[tipindex + 3] != 'rain':
				continue

			coin = splitmessage[tipindex + 5]
			if coin not in min_amount.keys():
				print('unknown coin ='+coin)
				continue

			try:
				amount = float(splitmessage[tipindex + 4])
			except:
				print('amount not float ='+splitmessage[tipindex + 4])
				continue
			if amount < min_amount[coin]:
				print('amount too low ='+splitmessage[tipindex + 4])
				continue
			if coin == 'doge':
				try:
					addresses = block_io_doge.get_my_addresses()
					users = []
					for user in addresses['data']['addresses']:
						if user['label'] in id2name.keys() and user['label'] != j['user']:
							users.append(user['label'])
					if len(splitmessage) > 6 and splitmessage[tipindex + 6] == 'online':
						try:
							user_on_list = sc.api_call("users.list", presence='1')
							for o in range(0,99,1):
								try:
									if user_on_list['members'][o]['presence'] == 'away':
										try:
											users.remove(user_on_list['members'][o]['id'])
										except:
											continue
								except:
									continue
						except:
							continue
					amounteach = amount / len(users)
					if amounteach < min_amount[coin]:
						print('amounteach too small ='+amounteach)
						continue
					tousers = str(','.join(user for user in users))
					toreadable = str(','.join(id2name[user] for user in users))
					toeach = str(','.join('%.8f'%amounteach for user in users))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_doge.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain doge')
					continue
					
			elif coin == 'ltc':
				try:
					addresses = block_io_ltc.get_my_addresses()
					users = []
					for user in addresses['data']['addresses']:
						if user['label'] in id2name.keys() and user['label'] != j['user']:
							users.append(user['label'])
					if len(splitmessage) > 6 and splitmessage[tipindex + 6] == 'online':
						try:
							user_on_list = sc.api_call("users.list", presence='1')
							for o in range(0,99,1):
								try:
									if user_on_list['members'][o]['presence'] == 'away':
										try:
											users.remove(user_on_list['members'][o]['id'])
										except:
											continue
								except:
									continue
						except:
							continue
					amounteach = amount / len(users)
					if amounteach < min_amount[coin]:
						print('amounteach too small ='+amounteach)
						continue
					tousers = str(','.join(user for user in users))
					toreadable = str(','.join(id2name[user] for user in users))
					toeach = str(','.join('%.8f'%amounteach for user in users))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_ltc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain ltc')
					continue
					
			elif coin == 'btc':
				try:
					addresses = block_io_btc.get_my_addresses()
					users = []
					for user in addresses['data']['addresses']:
						if user['label'] in id2name.keys() and user['label'] != j['user']:
							users.append(user['label'])
					if len(splitmessage) > 6 and splitmessage[tipindex + 6] == 'online':
						try:
							user_on_list = sc.api_call("users.list", presence='1')
							for o in range(0,99,1):
								try:
									if user_on_list['members'][o]['presence'] == 'away':
										try:
											users.remove(user_on_list['members'][o]['id'])
										except:
											continue
								except:
									continue
						except:
							continue
					amounteach = amount / len(users)
					if amounteach < min_amount[coin]:
						print('amounteach too small ='+amounteach)
						continue
					tousers = str(','.join(user for user in users))
					toreadable = str(','.join(id2name[user] for user in users))
					toeach = str(','.join('%.8f'%amounteach for user in users))
					print(id2name[j['user']]+' ('+j['user']+') made it rain on '+toreadable+' ('+tousers+') '+str(amount)+' ('+'%.8f' % amounteach+' each)');
					block_io_btc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' tipped  '+toreadable+' '+'%.8f' % amounteach+' '+coin+'!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to make it rain btc')
					continue

		# !tipbot withdraw
		elif command == 'withdraw':
			if len(splitmessage) < (tipindex + 4):
				continue

			amount = splitmessage[tipindex + 2]
			coin = splitmessage[tipindex + 3]
			address = splitmessage[tipindex + 4]

			if coin not in min_amount.keys():
				print('unknown coin ='+coin)
				continue

			print(id2name[j['user']]+' ('+j['user']+') withdraws '+amount+' '+coin+' to '+address)

			if coin == 'doge' and amount == 'all':
				try:			
					balance_doge = block_io_doge.get_address_balance(labels=j['user'])
					print(balance_doge['data']['available_balance'])
					fee = block_io_doge.get_network_fee_estimate(amounts=balance_doge['data']['available_balance'], to_addresses=address, priority='low')
					print(fee)
					balance_minus_fee = float(balance_doge['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_doge.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw doge')
						continue
			elif coin == 'doge':
				try:
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(splitexc[n])+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw doge')
						continue
			elif coin == 'ltc' and amount == 'all':	
				try:		
					balance_ltc = block_io_ltc.get_address_balance(labels=j['user'])
					print(balance_ltc['data']['available_balance'])
					fee = block_io_ltc.get_network_fee_estimate(amounts=balance_ltc['data']['available_balance'], to_addresses=address, priority='low')
					print(fee)
					balance_minus_fee = float(balance_ltc['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_ltc.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:				
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw ltc')
						continue
			elif coin == 'ltc':
				try:
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(splitexc[n])+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw ltc')
						continue
			elif coin == 'btc' and amount == 'all':
				try:			
					balance_btc = block_io_btc.get_address_balance(labels=j['user'])
					print(balance_btc['data']['available_balance'])
					fee = block_io_btc.get_network_fee_estimate(amounts=balance_btc['data']['available_balance'], to_addresses=address, priority='low')
					print(fee)
					balance_minus_fee = float(balance_btc['data']['available_balance']) - float(fee['data']['estimated_network_fee'])
					print(balance_minus_fee)
					block_io_btc.withdraw_from_labels(amounts=balance_minus_fee, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_btc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw btc')
						continue
			elif coin == 'btc':	
				try:
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address, priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(amount)+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=address, priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' withdrew '+str(splitexc[n])+' '+coin+' to '+address+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to withdraw btc')
						continue
					
		# tipbot shift
		elif command == 'shift':	
			if len(splitmessage) < (tipindex + 3):
				continue

			amount = splitmessage[tipindex + 2]
			coin = splitmessage[tipindex + 3]
			pairs = set(['btc_ltc', 'btc_doge', 'ltc_btc', 'ltc_doge', 'doge_btc', 'doge_ltc'])
			if coin not in pairs:
				print('unknown coin ='+coin)
				continue

			print(id2name[j['user']]+' ('+j['user']+') shifted '+amount+' '+coin)
			
			if coin == 'btc_ltc':
				try:
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_ltc['data']['address'], "pair":"btc_ltc", "returnAddress":address_btc['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(amount)+' btc to ltc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_btc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(splitexc[n])+' btc to ltc  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
						continue
			elif coin == 'btc_doge':
				try:
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_doge['data']['address'], "pair":"btc_doge", "returnAddress":address_btc['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(amount)+' btc to doge!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_btc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(splitexc[n])+' btc to doge!  :unicorn_face', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
			elif coin == 'ltc_doge':
				try:
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_doge['data']['address'], "pair":"ltc_doge", "returnAddress":address_ltc['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(amount)+' ltc to doge!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(splitexc[n])+' ltc to doge!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
			elif coin == 'ltc_btc':
				try:
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_btc['data']['address'], "pair":"ltc_btc", "returnAddress":address_ltc['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(amount)+' ltc to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_ltc.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(splitexc[n])+' ltc to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
			elif coin == 'doge_btc':
				try:
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_btc['data']['address'], "pair":"doge_btc", "returnAddress":address_doge['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(amount)+' doge to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=str(id2name[j['user']])+' shifted '+str(splitexc[n])+' doge to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
			elif coin == 'doge_ltc':
				try:
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_ltc['data']['address'], "pair":"doge_ltc", "returnAddress":address_doge['data']['address'], "apiKey":shapeshift_pubkey}
					print(payload)
					try:
						r = requests.post(url, data=payload)
						response = r.text
						jresponse = json.loads(response)
						print(jresponse)
					except:
						traceback.print_exc()
						print('failed generate shapeshift transaction')
						continue
					amount = float(''.join(ele for ele in splitmessage[tipindex + 2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=j['user']+' shifted '+str(amount)+' doge to ltc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					try:
						exc = traceback.format_exc()
						splitexc = exc.split()
						n = len(splitexc)-2
						print(splitexc[n])					
						block_io_doge.withdraw_from_labels(amounts=splitexc[n], from_labels=j['user'], to_addresses=jresponse['deposit'], priority='low')
						print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' shifted '+str(splitexc[n])+' doge to ltc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						print('failed to shift')
		# !tipbot addresses
		elif command == 'addresses':
			if len(splitmessage) < (tipindex + 2):
				continue

			coin = splitmessage[tipindex + 2]
			if coin not in min_amount.keys():
				print('unknown coin ='+coin)
				continue

			if coin == 'doge':
				try:
					addresses = block_io_doge.get_my_addresses()
					for address in addresses['data']['addresses']:
						if address['label'] not in id2name.keys():
							continue
						balance = block_io_doge.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel=j['channel'], text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to get doge addresses')
					continue
			elif coin == 'ltc':
				try:
					addresses = block_io_ltc.get_my_addresses()
					for address in addresses['data']['addresses']:
						if address['label'] not in id2name.keys():
							continue
						balance = block_io_ltc.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel=j['channel'], text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to get ltc addresses')
					continue
			elif coin == 'btc':
				try:
					addresses = block_io_btc.get_my_addresses()
					for address in addresses['data']['addresses']:
						if address['label'] not in id2name.keys():
							continue
						balance = block_io_btc.get_address_balance(addresses=address['address'])
						print(sc.api_call("chat.postMessage", channel=j['channel'], text='|'+id2name[address['label']]+'|-- :  '+address['address']+': '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					print('failed to get btc addresses')
					continue

		# !tipbot register
		elif command == 'register':
			try:
				block_io_doge.get_new_address(label=j['user'])
			except:
				traceback.print_exc()
				print('failed to create doge address for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				block_io_ltc.get_new_address(label=j['user'])
			except:
				traceback.print_exc()
				print('failed to create ltc address for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				block_io_btc.get_new_address(label=j['user'])
			except:
				traceback.print_exc()
				print('failed to create btc address for '+id2name[j['user']]+' ('+j['user']+')')

			print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' registered!  :tada:', username='pybot', icon_emoji=':robot_face:'))

		# !tipbot check
		elif command == 'check':
			try:
				balance = block_io_doge.get_address_balance(labels=j['user'])
				address = block_io_doge.get_address_by_label(label=j['user'])
				try:
					c_doge = requests.get(coincap_doge)
					c_text_doge = c_doge.text
					jc_doge = json.loads(c_text_doge)
					print('doge $'+str(jc_doge['usdPrice']))
					usd_doge = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_doge['usdPrice'])))
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' dogecoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' doge  ~$'+str(usd_doge), username='pybot', icon_emoji=':robot_face:'))
				except:
					c_doge = requests.get(cryptocomp_doge)
					c_text_doge = c_doge.text
					jc_doge = json.loads(c_text_doge)
					print('doge $'+str(jc_doge['Data'][0]['Price']))
					usd_doge = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_doge['Data'][0]['Price'])))
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' dogecoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' doge  ~$'+str(usd_doge), username='pybot', icon_emoji=':robot_face:'))
			except:
				traceback.print_exc()
				print('failed to check doge for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				balance = block_io_btc.get_address_balance(labels=j['user'])
				address = block_io_btc.get_address_by_label(label=j['user'])
				try:
					c_btc = requests.get(coincap_btc)
					c_text_btc = c_btc.text
					jc_btc = json.loads(c_text_btc)
					print('btc $'+str(jc_btc['usdPrice']))
					usd_btc = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_btc['usdPrice'])))
					print(usd_btc)
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' bitcoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' btc  ~$'+str(usd_btc), username='pybot', icon_emoji=':robot_face:'))
				except:
					c_btc = requests.get(cryptocomp_btc)
					c_text_btc = c_btc.text
					jc_btc = json.loads(c_text_btc)
					print('btc $'+str(jc_btc['Data'][0]['Price']))
					usd_btc = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_btc['Data'][0]['Price'])))
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' btccoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' btc  ~$'+str(usd_btc), username='pybot', icon_emoji=':robot_face:'))			
			except:
				traceback.print_exc()
				print('failed to check btc for '+id2name[j['user']]+' ('+j['user']+')')
			try:
				balance = block_io_ltc.get_address_balance(labels=j['user'])
				address = block_io_ltc.get_address_by_label(label=j['user'])
				try:
					c_ltc = requests.get(coincap_ltc)
					c_text_ltc = c_ltc.text
					jc_ltc = json.loads(c_text_ltc)
					print('ltc $'+str(jc_ltc['usdPrice']))
					usd_ltc = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_ltc['usdPrice'])))
					print(usd_ltc)
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' litecoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' ltc  ~$'+str(usd_ltc), username='pybot', icon_emoji=':robot_face:'))
				except:
					c_ltc = requests.get(cryptocomp_ltc)
					c_text_ltc = c_ltc.text
					jc_ltc = json.loads(c_text_ltc)
					print('ltc $'+str(jc_ltc['Data'][0]['Price']))
					usd_ltc = float("{0:.2f}".format(float(balance['data']['available_balance'])*float(jc_ltc['Data'][0]['Price'])))
					print(sc.api_call("chat.postMessage", channel=j['channel'], text=id2name[j['user']]+' ltccoin: - '+address['data']['address']+' - '+balance['data']['available_balance']+' ltc  ~$'+str(usd_ltc), username='pybot', icon_emoji=':robot_face:'))			
			except:
				traceback.print_exc()
				print('failed to check ltc for '+id2name[j['user']]+' ('+j['user']+')')

		# !tipbot help
		elif command == 'help':
			print(sc.api_call("chat.postMessage", channel=j['channel'], text='https://github.com/peoplma/slacktipbot', username='pybot', icon_emoji=':robot_face:'))

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
