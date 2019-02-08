import discord
from discord.ext import commands
import random
import json

waifus=json.loads(open("data/waifu/waifus.json").read())

class waifu:
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(pass_context=True)
	async def waifu(self, ctx):
		waifus2cuck=waifus
		author = ctx.message.author.mention
		user = ctx.message.author
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
		#Remove the '#' to enable
		#embed.add_field(name = "BWH", value = "{0},{1},{2}".format(waifuBust, waifuHip, waifuHeight))
		#embed.add_field(name = "Likes", value = "{0}".format(waifuLikes))
		#embed.add_field(name = "Dislikes", value = "{0}".format(waifuTrash)
		
		await self.bot.say(embed=embed)

def setup(client):
	client.add_cog(waifu(client))
