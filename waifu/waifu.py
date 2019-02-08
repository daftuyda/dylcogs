import discord
from discord.ext import commands
import random
import time
import json


waifus=json.loads(open("data/waifu/waifus.json").read())

class waifu:
	def __init__(self, client):
		self.client = client
		
	@commands.command(pass_context=True)
	async def waifu(self, ctx):
	
		waifus2cuck=waifus
		author = ctx.message.author.mention
		channel = ctx.message.channel
		
		waifu=waifus2cuck[random.randint(0, len(waifus2cuck)-1)]
			
		waifuName = waifu['name']
		animeName = waifu['series']['name']
		waifuImg = waifu['display_picture']
			
		await self.client.send_file(channel, waifuImg, content="%s, your waifu is **%s** (%s)" % (author, waifuName, animeName))

def setup(client):
	client.add_cog(waifu(client))
