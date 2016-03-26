# slacktipbot

# Syntax:

"!tipbot register" - generates a new address for user

"!tipbot addresses" - lists all registered users' addresses and their balances

"!tipbot tip (user, coin, amount)" - tips user indicated amount to their address

"!tipbot withdraw (coin, amount, address)" - withdraws indicated amount to indicated address.  Address must be the last word listed in command

"!tipbot help" - links to this readme

#Dependencies

[Block.io](https://github.com/BlockIo/block_io-python/blob/master/README.md):
`pip install block-io`

[Slackclient](https://github.com/slackhq/python-slackclient):
`pip install slackclient`

[Slacksocket](https://github.com/vektorlab/slacksocket)
`pip install slacksocket`

#Installation:
Install dependencies.  (Tested in python 3.4).  Create an account at [block.io](https://block.io/).  Add your secret_pin to the key_pin.py file, and get your API key and add that to the key_pin.py file.  In Slack, go to the Slack "custom integratrions" page (by clicking in the upper left of your chat and choosing "Apps and integrations") and add a "bot".  Get the API key and add that to the key_pin.py file.
