# slacktipbot

# Syntax:

"!tipbot register" - generates a new address for user

"!tipbot addresses" - lists all registered users' addresses and their balances

"!tipbot tip (user, coin, amount)" - tips user indicated amount to their address

"!tipbot withdraw (coin, amount, address)" - withdraws indicated amount to indicated address.  Address must be the last word listed in command

"!tipbot help" - links to this readme

#Dependencies:

[Block.io](https://github.com/BlockIo/block_io-python/blob/master/README.md):
`pip install block-io`

[Slackclient](https://github.com/slackhq/python-slackclient):
`pip install slackclient`

[Slacksocket](https://github.com/vektorlab/slacksocket)
`pip install slacksocket`

#Installation:
Install dependencies.  (Tested in python 3.4).  Create an account at [block.io](https://block.io/).  Add your secret_pin to the key_pin.py file, and get your API key and add that to the key_pin.py file.  In Slack, go to the Slack "custom integratrions" page (by clicking in the upper left of your chat and choosing "Apps and integrations") and add a "bot".  Get the API key and add that to the key_pin.py file.

#Usage:
Users will first need to "!tipbot register" for the bot to generate an address for them.  The user can then see their address with "!tipbot addresses".  Deposit to that address, and you can then tip to other registered users.  Or withdraw using "!tipbot withdraw".  All tips and withdraws are "on-chain".

#Security:
The bot operator has full control over everyone's addresses.  Users can withdraw to an address they control, and it is recommended to do so.  Significant amounts of money should not be stored in the slacktipbot address, even if you trust the bot operator completely.
