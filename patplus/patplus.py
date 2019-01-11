from discord.ext import commands
import random
import discord

class Pat:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def pat(self, context, member: discord.Member):
        """Pat your senpai/waifu!"""
        author = context.message.author.mention
        mention = member.mention
        
        pat = "**{0} got patted by {1}!**"
        
        choices = ['http://i.imgur.com/10VrpFZ.gif', 'http://i.imgur.com/x0u35IU.gif', 'http://i.imgur.com/0gTbTNR.gif', 'http://i.imgur.com/hlLCiAt.gif', 'http://i.imgur.com/sAANBDj.gif', 'http://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif', 'https://archive-media-0.nyafuu.org/c/image/1483/54/1483549839638.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-head-pat-gif-5.gif', 'https://media1.tenor.com/images/bb5608910848ba61808c8f28caf6ec7d/tenor.gif?itemid=11039783', 'https://steamuserimages-a.akamaihd.net/ugc/261598769614784180/DBDAB5E25FF6CFAC86EFB365F7AC605A52C81A1E/', 'https://thumbs.gfycat.com/MassiveNeglectedAustraliankestrel-small.gif', 'https://66.media.tumblr.com/8c20bf3900aba4187952196ce3b2ae86/tumblr_p2kzogLOZU1vajq0ro5_500.gif', 'https://i.pinimg.com/originals/a0/6d/65/a06d65ad49f019aaae3f30fb872df619.gif', 'http://30.media.tumblr.com/bde29ae19fa160f0fc7bc8f0dcf5308b/tumblr_n7t4ioLycK1rbnx7io1_500.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-head-pat-gif-9.gif', 'https://media1.tenor.com/images/dedb5720daef530caf9ea18e05b830a7/tenor.gif?itemid=12004190', 'https://66.media.tumblr.com/cadf248febe96afdd6869b7a95600abb/tumblr_onjo4cGrZE1vhnny1o1_500.gif', 'https://media.giphy.com/media/109ltuoSQT212w/giphy.gif', 'http://i.imgur.com/laEy6LU.gif', 'https://media.tenor.com/images/1d37a873edfeb81a1f5403f4a3bfa185/tenor.gif', 'https://data.whicdn.com/images/128044722/original.gif', 'https://i.pinimg.com/originals/2e/27/d5/2e27d5d124bc2a62ddeb5dc9e7a73dd8.gif', 'https://media1.tenor.com/images/9fa1e50a657ea2ece043de6e0e93ac8e/tenor.gif?itemid=10361558', 'https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif', 'https://media1.tenor.com/images/c0bcaeaa785a6bdf1fae82ecac65d0cc/tenor.gif?itemid=7453915', 'https://thumbs.gfycat.com/FlimsyDeafeningGrassspider-small.gif']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=pat.format(mention, author), colour=discord.Colour.blue())
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Pat(bot)
    bot.add_cog(n)
