from discord.ext import commands
import random
import discord

class Slapplus:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def slap(self, context, member: discord.Member):
        """Slap a bully!"""
        author = context.message.author.mention
        mention = member.mention
        
        slap = "**{0} slapped {1}!**"
        
        choices = ['http://i.imgur.com/6mOFy3v.gif', 'http://i.imgur.com/jb50TEF.gif', 'http://i.imgur.com/mDSjXer.gif', 'http://i.imgur.com/b8cytk1.gif', 'http://i.imgur.com/Ub8fT3G.gif', 'http://i.imgur.com/jNaAaxn.gif', 'https://i.imgur.com/PgXKJj9.gif', 'https://i.imgur.com/OEgCs9l.gif', 'https://i.imgur.com/bt2sb6g.gif', 'https://i.imgur.com/o6KVjWZ.gif', 'https://i.imgur.com/CLiuB5B.gif', 'https://i.imgur.com/9XOE4AI.gif', 'https://i.imgur.com/hSJWzfS.gif', 'https://i.imgur.com/3GNP0Sn.gif', 'https://i.imgur.com/tWedDrF.gif', 'https://i.imgur.com/yxlfY8E.gif', 'https://i.imgur.com/Lql2RJY.gif', 'https://i.imgur.com/Ov2tHZS.gif', 'https://i.imgur.com/GyKT70n.gif', 'https://i.imgur.com/8SnQVim.gif', 'https://i.imgur.com/ZUZlpU1.gif', 'https://i.imgur.com/CqZJIhq.gif', 'https://i.imgur.com/PaLyLJg.gif', 'https://i.imgur.com/YBp14vb.gif', 'https://i.imgur.com/Sr81YkU.gif', 'https://i.imgur.com/C6OxUUD.gif', 'https://i.imgur.com/0ySDfd3.gif', 'https://i.imgur.com/gddivs6.gif', 'https://i.imgur.com/eNiIck1.gif']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=slap.format(author, mention), colour=discord.Colour(0xba4b5b))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Slapplus(bot)
    bot.add_cog(n)
