import time
import json
import re
import traceback
from slacksocket import SlackSocket
from slackclient import SlackClient
from block_io import BlockIo
version = 2 # API version
from blockio_key_pin import *
block_io = BlockIo(blockio_api_key, blockio_secret_pin, version) 
ss = SlackSocket(slack_token,translate=False) # translate will lookup and replace user and channel IDs with their human-readable names. default true. 
sc = SlackClient(slack_token)

def main():
	time.sleep(2)
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
			if '!tipbot register' in str(j['text']):
				print(j['user'] + ' registered')
				reguser = sc.api_call("users.info", user=j['user'])
				print(reguser)
				block_io.get_new_address(label=j['user'])
				print(sc.api_call("chat.postMessage", channel="#general", text="You are registered "+reguser['user']['name']+" !  :tada:", username='pybot', icon_emoji=':robot_face:'))
			for (x, (usernames)) in enumeration:
				if '!tipbot tip ' in str(j['text']) and usernames in str(j['text']):
					for z in range(0,99,1):
						try:
							if users['members'][z]['name'] == usernames:
								amount = float(''.join(ele for ele in j['text'] if ele.isdigit() or ele == '.'))
								tippeduser = users['members'][z]['id']
								block_io.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_labels=tippeduser)
								print(j['user']+' tipped '+usernames)
								print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' tipped '+usernames+' '+str(amount)+' doge!  :moon:', username='pybot', icon_emoji=':robot_face:'))
						except:
							continue
			if '!tipbot withdraw ' in str(j['text']):
				print(splitmessage)
				address = splitmessage.pop()
				print(address)
				print(splitmessage)
				amount = float(''.join(ele for ele in splitmessage if ele.isdigit() or ele == '.'))
				print(amount)
				block_io.withdraw_from_labels(amounts=amount, from_labels=j['user'], to_addresses=address)
				print(j['user']+' withdrew to'+address)
				print(sc.api_call("chat.postMessage", channel="#general", text=j['user']+' withdrew '+str(amount)+' doge to '+str(address)+'!  :+1:', username='pybot', icon_emoji=':robot_face:'))
			if '!tipbot addresses' in str(j['text']):
				addresses = block_io.get_my_addresses()			
				for x in range(1,99,1):
					try:
						address = str(addresses['data']['addresses'][x]['address'])
						balance = block_io.get_address_balance(addresses=address)
						name = sc.api_call("users.info", user=addresses['data']['addresses'][x]['label'])
						print(sc.api_call("chat.postMessage", channel="#general", text='|l'+name['user']['name']+'|-- :  '+addresses['data']['addresses'][x]['address']+':  '+balance['data']['available_balance'], username='pybot', icon_emoji=':robot_face:'))
					except:
						continue
			#if '!tipbot help' in str(j['text']):
				#print(sc.api_call("chat.postMessage", channel="#general", text='|l!tipbot addresses|-- retrieves all registered users addresses and balances', username='pybot', icon_emoji=':robot_face:'))
def secondary():
	try:
		while True:
			main()
	except:
		traceback.print_exc()
		print('Resuming in 30sec...')
		time.sleep(2)
		print('Resumed')
while True:
	secondary()