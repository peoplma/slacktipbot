import time
import json
import re
import traceback
import requests
from slacksocket import SlackSocket
from slackclient import SlackClient
from block_io import BlockIo
version = 2 # API version
from key_pin import *
block_io_doge = BlockIo(blockio_api_doge_key, blockio_secret_pin, version) 
block_io_btc = BlockIo(blockio_api_btc_key, blockio_secret_pin, version)
block_io_ltc = BlockIo(blockio_api_ltc_key, blockio_secret_pin, version)
ss = SlackSocket(slack_token,translate=False) # translate will lookup and replace user and channel IDs with their human-readable names. default true. 
sc = SlackClient(slack_token)
url = 'https://shapeshift.io/shift'

def main():
	time.sleep(1)
	for event in ss.events():
		usernames = set()
		userids = set()
		users = sc.api_call("users.list")
		for i in range(0, 99, 1):
			try:
				usernames.add(users['members'][i]['name'])
				userids.add(users['members'][i]['id'])	
			except:
				continue
		enumeration = enumerate(usernames)		
		print(event.json)
		j = json.loads(event.json)
		print(j['type'])
		if j['type'] == 'message':
			splitmessage = j['text'].split( )
			print(splitmessage)
			print(j['text'])						

			########### FOR TIPPING #########
				
			for (x, (usernames)) in enumeration:
				if '!tipbot tip ' in str(j['text']) and usernames in str(j['text']) and 'doge' in str(j['text']):
					print(usernames)
					for z in range(0,99,1):
						try:
							print(users['members'][z]['name'])
							#tippeduser = users['members'][z]['id']
							#print(tippeduser)
							#print(usernames)
							if users['members'][z]['name'] == usernames:
								#print(tippeduser)
								text = j['text']
								textreplace = text.replace(usernames,'',1)
								amount = float(''.join(ele for ele in textreplace if ele.isdigit() or ele == '.'))
								tippeduser = users['members'][z]['id']
								block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_labels=tippeduser)
								print(tippeduser)
								print(j['user']+' tipped '+usernames)
								print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped '+usernames+' '+str(amount)+' doge!  :moon:', username='pybot', icon_emoji=':robot_face:'))
						except:
							traceback.print_exc()
							continue
				if '!tipbot tip ' in str(j['text']) and usernames in str(j['text']) and 'btc' in str(j['text']):
					print(usernames)
					for z in range(0,99,1):
						try:
							print(users['members'][z]['name'])
							#tippeduser = users['members'][z]['id']
							#print(tippeduser)
							#print(usernames)
							if users['members'][z]['name'] == usernames:
								#print(tippeduser)
								text = j['text']
								textreplace = text.replace(usernames,'',1)
								amount = float(''.join(ele for ele in textreplace if ele.isdigit() or ele == '.'))
								tippeduser = users['members'][z]['id']
								block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_labels=tippeduser)
								print(tippeduser)
								print(j['user']+' tipped '+usernames)
								print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped '+usernames+' '+str(amount)+' btc!  :moon:', username='pybot', icon_emoji=':robot_face:'))
						except:
							traceback.print_exc()
							continue
				if '!tipbot tip ' in str(j['text']) and usernames in str(j['text']) and 'ltc' in str(j['text']):
					print(usernames)
					for z in range(0,99,1):
						try:
							print(users['members'][z]['name'])
							#tippeduser = users['members'][z]['id']
							#print(tippeduser)
							#print(usernames)
							if users['members'][z]['name'] == usernames:
								#print(tippeduser)
								text = j['text']
								textreplace = text.replace(usernames,'',1)
								amount = float(''.join(ele for ele in textreplace if ele.isdigit() or ele == '.'))
								tippeduser = users['members'][z]['id']
								block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_labels=tippeduser)
								print(tippeduser)
								print(j['user']+' tipped '+usernames)
								print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped '+usernames+' '+str(amount)+' ltc!  :moon:', username='pybot', icon_emoji=':robot_face:'))
						except:
							traceback.print_exc()
							continue
			
			########### FOR SHAPESHIFT ##########
			
			if '!tipbot shift' in str(j['text']) and 'btc_ltc' in str(j['text']):
				try:
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_ltc['data']['address'], "pair":"btc_ltc", "returnAddress":address_btc['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' btc to ltc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot shift' in str(j['text']) and 'btc_doge' in str(j['text']):
				try:
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_doge['data']['address'], "pair":"btc_doge", "returnAddress":address_btc['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' btc to doge!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot shift' in str(j['text']) and 'ltc_doge' in str(j['text']):
				try:
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_doge['data']['address'], "pair":"ltc_doge", "returnAddress":address_ltc['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' ltc to doge!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot shift' in str(j['text']) and 'ltc_btc' in str(j['text']):
				try:
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_btc['data']['address'], "pair":"ltc_btc", "returnAddress":address_ltc['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' ltc to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot shift' in str(j['text']) and 'doge_btc' in str(j['text']):
				try:
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_btc['data']['address'], "pair":"doge_btc", "returnAddress":address_doge['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' doge to btc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot shift' in str(j['text']) and 'doge_ltc' in str(j['text']):
				try:
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					payload = {"withdrawal":address_ltc['data']['address'], "pair":"doge_ltc", "returnAddress":address_doge['data']['address']}
					print(payload)
					r = requests.post(url, data=payload)
					response = r.text
					jresponse = json.loads(response)
					print(jresponse)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=jresponse['deposit'])
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' shifted '+str(amount)+' doge to ltc!  :unicorn_face:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue	
					
			########### FOR DOGECOIN #########
			
			if '!tipbot make it rain ' in str(j['text']) and 'doge' in str(j['text']):
				try:
					addresses = block_io_doge.get_my_addresses()
					textamount = splitmessage.pop();
					amount = float(''.join(ele for ele in textamount if ele.isdigit() or ele == '.'))
					amounteach = (amount - 1) / (len(addresses['data']['addresses']) - 2)
								#(amount - fee) / (number of addresses - current user)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(tousers)
					print(toeach)
					block_io_doge.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped everyone '+'%.8f' % amounteach+' doge!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot withdraw ' in str(j['text']) and 'doge' in str(j['text']):
				print(splitmessage)
				address = splitmessage.pop()
				print(address)
				print(splitmessage)
				amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
				print(amount)
				block_io_doge.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
				print(j['user']+' withdrew ' +str(amount)+' to '+str(address))
				print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' withdrew '+str(amount)+' doge to '+str(address)+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
			if '!tipbot doge addresses' in str(j['text']):
				addresses = block_io_doge.get_my_addresses()			
				for x in range(1,99,1):
					try:
						address = str(addresses['data']['addresses'][x]['address'])
						balance = block_io_doge.get_address_balance(addresses=address)
						name = sc.api_call("users.info", user=addresses['data']['addresses'][x]['label'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|l'+name['user']['name']+'|-- :  '+addresses['data']['addresses'][x]['address']+':  '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						continue
						
			########## FOR BITCOIN ############
			
			if '!tipbot make it rain ' in str(j['text']) and 'btc' in str(j['text']):
				try:
					addresses = block_io_btc.get_my_addresses()
					textamount = splitmessage.pop();
					amount = float(''.join(ele for ele in textamount if ele.isdigit() or ele == '.'))
					amounteach = (amount - 1) / (len(addresses['data']['addresses']) - 2)
								#(amount - fee) / (number of addresses - current user)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(tousers)
					print(toeach)
					block_io_btc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped everyone '+'%.8f' % amounteach+' btc!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot withdraw ' in str(j['text']) and 'btc' in str(j['text']) and 'all' not in str(j['text']):
				try:
					print(splitmessage)
					address = splitmessage.pop()
					print(address)
					print(splitmessage)
					amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
					print(amount)
					block_io_btc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
					print(j['user']+' withdrew ' +str(amount)+' to '+str(address))
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' withdrew '+str(amount)+' btc to '+str(address)+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue					
			if '!tipbot withdraw all' in str(j['text']) and 'btc' in str(j['text']):
				try:
					address = splitmessage.pop()
					balance_btc = block_io_btc.get_address_balance(labels=j['user'])
					#fee = block_io_btc.get_network_fee_estimate(amounts=balance_btc, to_addresses=address)
					#fee = balance_btc['data']['available_balance']
					#balance_btc -= 0.0005
					#print(minus_fee)
					withdraw = block_io_btc.withdraw_from_labels(amounts=balance_btc['data']['available_balance'], from_labels=j['user'], to_addresses=address)
					print(withdraw)
				except:
					block_io_btc.withdraw_from_labels(amounts=withdraw['data']['max_withdrawal_available'], from_labels=j['user'], to_addresses=address)
					print(j['user']+' withdrew ' +withdraw['data']['max_withdrawal_available']+' to '+address)
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' withdrew '+str(withdraw['data']['max_withdrawal_available'])+' btc to '+str(address)+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
					traceback.print_exc()
					continue
			if '!tipbot btc addresses' in str(j['text']):
				addresses = block_io_btc.get_my_addresses()			
				for x in range(1,99,1):
					try:
						address = str(addresses['data']['addresses'][x]['address'])
						balance = block_io_btc.get_address_balance(addresses=address)
						name = sc.api_call("users.info", user=addresses['data']['addresses'][x]['label'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|l'+name['user']['name']+'|-- :  '+addresses['data']['addresses'][x]['address']+':  '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						continue
			
			########## FOR LITECOIN ################
			
			if '!tipbot make it rain ' in str(j['text']) and 'ltc' in str(j['text']):
				try:
					addresses = block_io_ltc.get_my_addresses()
					textamount = splitmessage.pop();
					amount = float(''.join(ele for ele in textamount if ele.isdigit() or ele == '.'))
					amounteach = (amount - 1) / (len(addresses['data']['addresses']) - 2)
								#(amount - fee) / (number of addresses - current user)
					tousers = str(','.join(addr['label'] for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					toeach = str(','.join('%.8f' % amounteach for addr in addresses['data']['addresses'] if (addr['label'] != j['user'] and addr['label'] != 'default')))
					print(tousers)
					print(toeach)
					block_io_ltc.withdraw_from_labels(amounts=toeach, from_labels=j['user'], to_labels=tousers)
					print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped everyone '+'%.8f' % amounteach+' ltc!  :moon:', username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot withdraw ' in str(j['text']) and 'ltc' in str(j['text']):
				print(splitmessage)
				address = splitmessage.pop()
				print(address)
				print(splitmessage)
				amount = float(''.join(ele for ele in splitmessage[2] if ele.isdigit() or ele == '.'))
				print(amount)
				block_io_ltc.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
				print(j['user']+' withdrew ' +str(amount)+' to '+str(address))
				print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' withdrew '+str(amount)+' ltc to '+str(address)+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
			if '!tipbot ltc addresses' in str(j['text']):
				addresses = block_io_btc.get_my_addresses()			
				for x in range(1,99,1):
					try:
						address = str(addresses['data']['addresses'][x]['address'])
						balance = block_io_ltc.get_address_balance(addresses=address)
						name = sc.api_call("users.info", user=addresses['data']['addresses'][x]['label'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|l'+name['user']['name']+'|-- :  '+addresses['data']['addresses'][x]['address']+':  '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
					except:
						traceback.print_exc()
						continue

			############# END COIN SPECIFIC ################
			
			if '!tipbot register' in str(j['text']):
				print(j['user'] + ' registered')
				reguser = sc.api_call("users.info", user=j['user'])
				print(reguser)
				block_io_doge.get_new_address(label=j['user'])
				block_io_btc.get_new_address(label=j['user'])
				block_io_ltc.get_new_address(label=j['user'])
				print(sc.api_call("chat.postMessage", channel="#general", text="You are registered "+reguser['user']['name']+" !  :tada:", username='pybot', icon_emoji=':robot_face:'))
			if '!tipbot check' in str(j['text']):
				try:
					balance_doge = block_io_doge.get_address_balance(labels=j['user'])
					address_doge = block_io_doge.get_address_by_label(label=j['user'])
					print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s doge' % (j['user']+' dogecoin: ', address_doge['data']['address'], balance_doge['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
					balance_btc = block_io_btc.get_address_balance(labels=j['user'])
					address_btc = block_io_btc.get_address_by_label(label=j['user'])
					print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s btc' % (j['user']+' bitcoin: ', address_btc['data']['address'], balance_btc['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
					balance_ltc = block_io_ltc.get_address_balance(labels=j['user'])
					address_ltc = block_io_ltc.get_address_by_label(label=j['user'])
					print(sc.api_call("chat.postMessage", channel="#general", text='%s - %s - %s ltc' % (j['user']+' litecoin: ', address_ltc['data']['address'], balance_ltc['data']['available_balance']), username='pybot', icon_emoji=':robot_face:'))
				except:
					traceback.print_exc()
					continue
			if '!tipbot help' in str(j['text']):
				print(sc.api_call("chat.postMessage", channel="#general", text='https://github.com/peoplma/slacktipbot', username='pybot', icon_emoji=':robot_face:'))
			if 'tipbot kill all humans' in str(j['text']):
				print(sc.api_call("chat.postMessage", channel="#general", text='http://i.imgur.com/nwLy8Rd.jpg', username='pybot', icon_emoji=':robot_face:'))				
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
