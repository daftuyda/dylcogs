import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
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
		user = ctx.message.author
		self.prefix = "data/waifu/prefix.json"
		self.imagenius = dataIO.load_json(self.prefix)
		prefix = self.imagenius["MAINPREFIX"]
		waifu=waifus2cuck[random.randint(0, len(waifus2cuck)-1)]
			
		waifuName = waifu['name']
		animeName = waifu['series']['name']
		waifuImg = waifu['display_picture']
		waifuHeight = waifu['height']
		waifuHip = waifu['hip']
		waifuBust = waifu['bust']
		waifuLikes = waifu['likes']
		waifuTrash = waifu['trash']

		waifuDesc = "{0}, your waifu is **{1}**"

		embed = discord.Embed(description=waifuDesc.format(author, waifuName),colour=user.colour)
		embed.set_image(url=waifuImg)
		embed.add_field(name = "From:", value = "{0}".format(animeName))
		#embed.add_field(name = "BWH", value = "{0},{1},{2}".format(waifuBust, waifuHip, waifuHeight))
		#embed.add_field(name = "Likes", value = "{0}".format(waifuLikes))
		#embed.add_field(name = "Dislikes", value = "{0}".format(waifuTrash)
		
		await self.client.say(embed=embed)

		start = time.time()
			
		while time.time()<(start+20):
			m = await self.client.wait_for_message(channel=channel, timeout=1)
			if m is None:
				continue
			if (m.content).lower() == "{0}claim".format(prefix):
				await self.client.say("%s has added **%s** to their harem!" % (m.author.mention, waifuName))
				break
			if m.content == "{0}waifu".format(prefix):
					return

def setup(client):
	client.add_cog(waifu(client))
