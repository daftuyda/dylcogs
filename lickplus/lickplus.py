from discord.ext import commands
import random
import discord

class lick:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def lick(self, context, member: discord.Member):
		"""Great for lewding!"""
		author = context.message.author.mention
		mention = member.mention
		lick = "**{0} licks {1}!**"
		choices = ['https://media.giphy.com/media/12MEJ2ArZc23cY/source.gif', 'http://gifimage.net/wp-content/uploads/2017/09/anime-lick-gif-12.gif', 'https://i.pinimg.com/originals/e6/1d/a7/e61da774938e4f209818edcbc0d4a671.gif', 'https://68.media.tumblr.com/b80cda919b3309f2cb974635e429db57/tumblr_osuazevFcj1qcsnnso1_500.gif', 'https://i.imgur.com/p27RXEN.gif', 'https://i.imgur.com/npNvmDP.gif', 'https://i.imgur.com/NyK3k6V.gif', 'https://i.imgur.com/RZYi9ll.gif', 'https://i.imgur.com/EpVe8XX.gif', 'https://i.imgur.com/tx23QSV.gif', 'https://i.imgur.com/QTc6Gh2.gif', 'https://i.imgur.com/Zm2EaKt.gif', 'https://i.imgur.com/jcVj0cp.gif', 'https://i.imgur.com/sHtmOQ5.gif', 'https://i.imgur.com/yDoBzqB.gif', 'https://i.imgur.com/f9huvqh.gif', 'https://i.imgur.com/0XnCkG1.gif', 'https://i.imgur.com/HqX8PEq.gif', 'https://i.imgur.com/788kNzY.gif', 'https://i.imgur.com/aPgWLOy.gif', 'https://i.imgur.com/9kOXvm8.gif', 'https://i.imgur.com/GdGzL29.gif', 'https://i.imgur.com/953yQU0.gif', 'https://i.imgur.com/m5Knxos.gif', 'https://i.imgur.com/rN65tBb.gif', 'https://i.imgur.com/OTkvv7G.gif', 'https://i.imgur.com/jtisRbp.gif', 'https://i.imgur.com/sIDDLuJ.gif', 'https://i.imgur.com/nuNgm8g.gif', 'https://i.imgur.com/ToMSi1D.gif']
		image = random.choice(choices)
		embed = discord.Embed(description=lick.format(author, mention), colour=discord.Colour(0xba4b5b))
		embed.set_image(url=image)
		await self.bot.say(embed=embed)

def setup(bot):
	n = lick(bot)
	bot.add_cog(n)
