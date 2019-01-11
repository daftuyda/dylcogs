from discord.ext import commands
import random
import discord

class tickleplus:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def tickle(self, context, member: discord.Member):
		author = context.message.author.mention
		mention = member.mention
		tickle = "**{0} tickles {1}!**"
		choices = ['https://i.imgur.com/6IrniKg.gif', 'https://i.imgur.com/KKjawkx.gif', 'https://i.imgur.com/2h7F6yo.gif', 'https://78.media.tumblr.com/bec329b48b863f2e211ca7d4e3396ce9/tumblr_og7p24fa3R1vpbklao8_r6_500.gif', 'https://i.pinimg.com/originals/f6/81/93/f68193ba7eaeccc3d999b1da956b2fa3.gif', 'https://d2w9rnfcy7mm78.cloudfront.net/3041395/original_86b9e4adc77ef6e4cadfb42c44f566c8.gif?1542224582', 'https://uploads.disquscdn.com/images/6a6eba6bfd303bbf5a870cbdcfc124e2361b720baa30680c7d31e77e0608de78.gif', 'https://media1.tenor.com/images/8805429ac9516122813365301fbf768c/tenor.gif?itemid=7374727', 'https://media.giphy.com/media/9WTZAFpX4V4FG/giphy.gif', 'https://media.giphy.com/media/IRKHf3hD2xsre/giphy.gif', 'https://media1.tenor.com/images/74666b5f038f46eb0147e660b5e6216b/tenor.gif', 'https://myanimelist.cdn-dena.com/s/common/uploaded_files/1482023376-9b6557f8f70ce4ba9c2917b78ce76137.gif', 'http://66.media.tumblr.com/87bd396eb0f6884d421b9ef20dd93d67/tumblr_mnzybe6KKg1qd87hlo1_500.gif', 'http://pa1.narvii.com/5997/284518131a267b5641cc6f3f9618da18466406e4_hq.gif', 'https://1eu.funnyjunk.com/gifs/Pretty+much+anytime+i+get+tickled+i+dont+like+being_b9d6a7_5127494.gif', 'http://orig13.deviantart.net/0fef/f/2013/242/8/f/sekaiichi_hatsukoi_tickle_fight_by_jerseycar-d6ke74l.gif', 'http://i232.photobucket.com/albums/ee231/Asahina-Mikuru/Mikuru%20-%20Gif%20Animados/nocovereu7.gif', 'http://i.imgur.com/KQwAroV.gif', 'http://vignette2.wikia.nocookie.net/tora-dora/images/2/2f/Minori_trying_to_tickle_Ami.gif', 'http://i.giphy.com/vf5RXzqGIWrZu.gif', 'http://orig15.deviantart.net/5dd6/f/2013/262/a/8/fennekinchu_by_lopmon1990-d6mydzl.gif', 'http://data.whicdn.com/images/70218960/large.gif', 'https://thumbs.gfycat.com/DaringGrossJellyfish-size_restricted.gif', 'https://media1.tenor.com/images/d38554c6e23b86c81f8d4a3764b38912/tenor.gif', 'https://media1.tenor.com/images/fea79fed0168efcaf1ddfb14d8af1a6d/tenor.gif', 'https://media.tenor.com/images/2e3bcdc3423c4b97dbdf2225fd3d6caf/tenor.gif']
		image = random.choice(choices)
		embed = discord.Embed(description=tickle.format(author, mention), colour=discord.Colour(0xba4b5b))
		embed.set_image(url=image)
		await self.bot.say(embed=embed)

def setup(bot):
	n = tickleplus(bot)
	bot.add_cog(n)
