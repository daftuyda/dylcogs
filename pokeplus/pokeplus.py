from discord.ext import commands
import random
import discord

class poke:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def poke(self, context, member: discord.Member):
        """poke someone!"""
        author = context.message.author.mention
        mention = member.mention
        
        poke = "**{0} poked {1}!**"
        
        choices = ['https://pa1.narvii.com/6021/b50b8078fa1d8e8f6d2ebfb085f106c642141723_hq.gif', 'https://media1.tenor.com/images/8fe23ec8e2c5e44964e5c11983ff6f41/tenor.gif', 'https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif', 'https://media.giphy.com/media/pWd3gD577gOqs/giphy.gif', 'http://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-12.gif', 'https://i.gifer.com/S00v.gif', 'https://i.imgur.com/1NMqz0i.gif', 'https://i.pinimg.com/originals/ec/d5/db/ecd5db48f5bdfb9b67f86f2094554839.gif', 'https://pa1.narvii.com/6021/b50b8078fa1d8e8f6d2ebfb085f106c642141723_hq.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-6.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-10.gif', 'https://media1.tenor.com/images/76e377271bf00ba61d954b2752713596/tenor.gif?itemid=5075308', 'https://i.pinimg.com/originals/b4/95/fb/b495fb19f4b9a1b04f48297b676c497b.gif', 'http://i.imgur.com/rxsyBWA.jpg', 'https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-9.gif', 'https://i.pinimg.com/originals/26/65/74/266574c657accd6c7e8452a7b9d9dc47.gif', 'https://thumbs.gfycat.com/EnlightenedInferiorAfricanaugurbuzzard-size_restricted.gif', 'https://data.whicdn.com/images/113023956/original.gif', 'https://media1.tenor.com/images/e8b25e7d069c203ea7f01989f2a0af59/tenor.gif?itemid=12011027', 'https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-12.gif', 'https://media0.giphy.com/media/hdt32CBL7MsOA/source.gif', 'https://media1.tenor.com/images/3b2bfd09965bd77f2a8cb9ba59cedbe4/tenor.gif?itemid=5607667', 'https://media1.tenor.com/images/fd46d903c4a20a7e82519a78f15b2750/tenor.gif?itemid=8562185', 'https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif', 'https://media1.tenor.com/images/3b9cffb5b30236f678fdccf442006a43/tenor.gif?itemid=7739077', 'https://media1.tenor.com/images/1236e0d70c6ee3ea91d414bcaf9f3aa4/tenor.gif?itemid=5015314']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=poke.format(author, mention), colour=discord.Colour(0xba4b5b))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = poke(bot)
    bot.add_cog(n)
