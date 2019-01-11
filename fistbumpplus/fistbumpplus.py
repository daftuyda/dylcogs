from discord.ext import commands
import random
import discord

class fistbumpplus:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def fistbump(self, context, member: discord.Member):
        """Give someone a fistbump with a gif :)"""
        author = context.message.author.mention
        mention = member.mention
        
        hug = "**{0} gave {1} a fistbump!**"
        
        choices = ['https://i.gifer.com/UPQ.gif', 'https://data.whicdn.com/images/279989055/original.gif', 'https://i.gifer.com/3QdW.gif', 'https://i.pinimg.com/originals/d3/94/6e/d3946e0fc719b6aaaffbb784f693663a.gif', 'https://media1.tenor.com/images/0bfae47add0180fd93b52ebb8bf89dd4/tenor.gif?itemid=5047789', 'https://vignette.wikia.nocookie.net/degrassi/images/f/f1/Gray_and_Natsu_fist_bump.gif/revision/latest?cb=20141021214843', 'https://i.gifer.com/OJ5.gif', 'http://images6.fanpop.com/image/photos/36600000/Anime-image-anime-36615672-500-250.gif', 'https://animebuzzel.files.wordpress.com/2016/09/issei_and_vali_bumping_fists.gif', 'https://media1.tenor.com/images/943f8a35a4cde5dc31dc0cda4bf175f3/tenor.gif?itemid=4927241', 'https://i.pinimg.com/originals/4e/5b/07/4e5b0761a9410cc9802ab9cc068c39d7.gif', 'https://66.media.tumblr.com/7b62d4d365b261636cbd67352d2bb7dd/tumblr_o67utr1JUK1sxfvy5o1_500.gif', 'https://i.pinimg.com/originals/85/d1/de/85d1decf34210f9bc82ecffb0d5860ec.gif', 'https://pa1.narvii.com/6057/e3fe94ab50b1533daaef7ae3a96b9363f4abdcac_hq.gif', 'https://media.moddb.com/images/groups/1/25/24269/ezgif-1061391309.gif', 'https://media1.tenor.com/images/7bda5c36ddaaf534277dec100d7933f8/tenor.gif?itemid=3553173', 'https://media.giphy.com/media/10gHM7SWWMi8hi/giphy.gif', 'https://media1.tenor.com/images/64d186a0bfb932f9a48ecb768f2ed76f/tenor.gif?itemid=6097581', 'https://i.gifer.com/SfRk.gif', 'https://thumbs.gfycat.com/CloudyFlamboyantBoilweevil-small.gif', 'https://media1.tenor.com/images/6bd921415f5a22ccd5d5d77613c92b3e/tenor.gif?itemid=5076745', 'https://media.giphy.com/media/14ubGFMWtxBiVy/giphy.gif', 'https://media1.tenor.com/images/eeda515e9e23604a46565ae7ff90dfb4/tenor.gif?itemid=10380419']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=hug.format(author, mention), colour=discord.Colour(0xba4b5b))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = fistbumpplus(bot)
    bot.add_cog(n)
