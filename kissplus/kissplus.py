from discord.ext import commands
import random
import discord

class Kissplus:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def kiss(self, context, member: discord.Member):
        """Kiss your senpai/waifu!"""
        author = context.message.author.mention
        mention = member.mention
        
        kiss = "**{0} gave {1} a kiss!**"
        
        choices = ['http://i.imgur.com/0D0Mijk.gif', 'http://i.imgur.com/TNhivqs.gif', 'http://i.imgur.com/3wv088f.gif', 'http://i.imgur.com/7mkRzr1.gif', 'http://i.imgur.com/8fEyFHe.gif', 'https://i.imgur.com/lVFs5bN.gif', 'https://i.imgur.com/IJkmQHi.gif', 'https://i.imgur.com/IcDDL7K.gif', 'https://i.imgur.com/qmZXhyA.gif', 'https://i.imgur.com/gQ1euon.gif', 'https://i.imgur.com/DMjxLlV.gif', 'https://i.imgur.com/34PIb1U.gif', 'https://i.imgur.com/c47ikky.gif', 'https://i.imgur.com/Kx6WHDV.gif', 'https://i.imgur.com/zOAPUsL.gif', 'https://i.imgur.com/IoOlxwl.gif', 'https://i.imgur.com/LgxKuOD.gif', 'https://i.imgur.com/MME0HdU.gif', 'https://i.imgur.com/wQjoQEl.gif', 'https://i.imgur.com/IeghH6n.gif', 'https://i.imgur.com/jeD4xw7.gif', 'https://i.imgur.com/KxYts4g.gif', 'https://i.imgur.com/d7Uyw4P.gif', 'https://i.imgur.com/lciEUIu.gif', 'https://i.imgur.com/CAjkEiK.gif']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=kiss.format(author, mention), colour=discord.Colour.blue())
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Kissplus(bot)
    bot.add_cog(n)
