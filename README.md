# slacktipbot

# Syntax:

"!tipbot register" - generates a new address for user

"!tipbot check" - shows address and balance for user

"!tipbot addresses _coin_" - lists all registered users' addresses and their balances by coin

"!tipbot tip _amount_ _coin_ _users_" - tips users indicated amount to their address

"!tipbot make it rain _amount_ _coin_" - tips everyone registered a share of indicated amount

"!tipbot withdraw _amount_ _coin_ _address_" - withdraws indicated amount to indicated address

"!tipbot help" - links to this readme

#Dependencies:

[Block.io](https://github.com/BlockIo/block_io-python/blob/master/README.md):
`pip install block-io`

[Slackclient](https://github.com/slackhq/python-slackclient):
`pip install slackclient`

[Slacksocket](https://github.com/vektorlab/slacksocket)
`pip install slacksocket`

#Installation:
Install dependencies.  Then `git clone https://github.com/peoplma/slacktipbot`  (Tested in python 3.4).  Create an account at [block.io](https://block.io/).  Add your secret_pin to the key_pin.py file, and get your API key and add that to the key_pin.py file.  In Slack, go to the Slack "custom integratrions" page (by clicking in the upper left of your chat and choosing "Apps and integrations") and add a "bot".  Get the API key and add that to the key_pin.py file.

#Usage:
Users will first need to "!tipbot register" for the bot to generate an address for them.  The user can then see their address with "!tipbot addresses".  Deposit to that address, and you can then tip to other registered users.  Or withdraw using "!tipbot withdraw".  All tips and withdraws are "on-chain".

The free account at block.io allows up to 100 different addresses, so 99 users can be served an address in your slack group.  If you want more, you'll need to get a paid block.io account.  If you have multiple slack groups, it is highly recommended that you create a new block.io account for each slack group you want to run the tipbot in.  You'll need seperate instances of the tipbot for each slack group.

#Security:
The bot operator has full control over everyone's addresses (that's you, not me, unless I set up the bot in your slack channel).  Users can withdraw to an address they control, and it is recommended to do so.  Significant amounts of money should not be stored in the slacktipbot address, even if you trust the bot operator completely.
