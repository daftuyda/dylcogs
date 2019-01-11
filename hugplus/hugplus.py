
from discord.ext import commands
import random
import discord

class Hug:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def hug(self, context, member: discord.Member):
        """Hug your senpai/waifu!"""
        author = context.message.author.mention
        mention = member.mention
        
        hug = "**{0} gave {1} a hug!**"
        
        choices = ['http://i.imgur.com/sW3RvRN.gif', 'http://i.imgur.com/gdE2w1x.gif', 'http://i.imgur.com/zpbtWVE.gif', 'http://i.imgur.com/ZQivdm1.gif', 'http://i.imgur.com/MWZUMNX.gif', 'https://i.imgur.com/hdFAGrL.gif', 'https://i.imgur.com/v9WYIAs.gif', 'https://i.imgur.com/gtnTChr.gif', 'https://i.imgur.com/9dU92Lm.gif', 'https://i.imgur.com/8Tzoeid.gif', 'https://i.imgur.com/Y6eaBQU.gif', 'https://i.imgur.com/tVE5U3a.gif', 'https://i.imgur.com/Mr7lZE0.gif', 'https://i.imgur.com/3981xrx.gif', 'https://i.imgur.com/XFfXuw5.gif', 'https://i.imgur.com/ynOmDCq.gif', 'https://i.imgur.com/KVm2tVY.gif', 'https://i.imgur.com/1WRUk6l.gif', 'https://i.imgur.com/J4HhVHz.gif', 'https://i.imgur.com/8MqA36p.gif', 'https://i.imgur.com/abKOQX0.gif', 'https://i.imgur.com/ydt9q2y.gif', 'https://i.imgur.com/YnKQyr0.gif', 'https://i.imgur.com/UcN6CQv.gif', 'https://i.imgur.com/jS65bm6.gif', 'https://i.imgur.com/ZIcCSz9.gif', 'https://i.imgur.com/lZDR89f.gif', 'https://i.imgur.com/AfLxed8.gif', 'https://i.imgur.com/v8ZtLgE.gif', 'https://i.imgur.com/9vRcI8a.gif', 'https://i.imgur.com/iEkTFVl.gif']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=hug.format(author, mention), colour=discord.Colour.blue())
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Hug(bot)
    bot.add_cog(n)
