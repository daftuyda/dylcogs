from discord.ext import commands
import random
import discord

class Dance:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def dance(self, context):
        """Just busting some moves."""
        author = context.message.author.mention
        
        dance = "**{0} busted out some moves!**"
        
        choices = ['https://dumielauxepices.net/sites/default/files/moves-clipart-fun-dance-690740-7350111.gif', 'http://4.bp.blogspot.com/-nrND9r2XzXI/UYFUUEujO2I/AAAAAAAASv0/Qur9_hnN6zQ/s1600/tumblr_mcpydmuee71rukbdkjs.gif', 'https://i.imgur.com/QzAywqY.gif', 'https://media.giphy.com/media/Y0DUUpYzi5Hy0/giphy.gif', 'https://img.fireden.net/a/image/1490/99/1490995058511.gif', 'https://38.media.tumblr.com/2f7473d810f7e91a5b3cea909a0d97c3/tumblr_n2swbzGw8A1ttmhcxo1_500.gif', 'https://data.whicdn.com/images/77772130/original.gif', 'https://img.fireden.net/a/image/1450/97/1450975684154.gif', 'https://img.fireden.net/a/image/1451/70/1451705454260.gif', 'http://gifimage.net/wp-content/uploads/2017/07/anime-girl-dancing-gif-12.gif', 'https://img.fireden.net/a/image/1451/70/1451705566355.gif', 'http://images6.fanpop.com/image/photos/33500000/anime-dancer-msyugioh123-33558535-500-223.gif', 'https://i.makeagif.com/media/7-04-2015/Cqxepz.gif', 'https://media.giphy.com/media/113LvPFzgeKReo/giphy.gif', 'https://media1.tenor.com/images/c9dc41cbdcf8ab55601ab762b564c91a/tenor.gif', 'https://media1.tenor.com/images/8d29986572c4a8d53a3196dda017b62a/tenor.gif', 'https://i.imgur.com/UDh4lLL.gif', 'https://thumbs.gfycat.com/ImpoliteIllinformedGermanwirehairedpointer-size_restricted.gif', 'https://data.whicdn.com/images/219671347/original.gif', 'https://img.fireden.net/a/image/1451/01/1451017036455.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-dance-gif-10.gif', 'https://data.whicdn.com/images/86167127/original.gif', 'https://i.pinimg.com/originals/97/42/ef/9742ef85f9b6da099525be42f2d6028e.gif', 'https://media.giphy.com/media/ZBG5f8jp3wFHy/giphy.gif', 'https://vignette.wikia.nocookie.net/legomessageboards/images/1/11/Anime_dance.gif', 'https://thumbs.gfycat.com/AllFantasticKiwi-small.gif', 'https://i.kym-cdn.com/photos/images/newsfeed/001/115/816/936.gif', 'https://media.giphy.com/media/f5yjEgDE324ta/giphy.gif', 'https://i.kym-cdn.com/photos/images/newsfeed/000/984/780/778.gif', 'http://i.imgur.com/tKWABYR.gif', 'https://i.pinimg.com/originals/3e/45/c1/3e45c1e7fe5d4415349e07672ca995a6.gif', 'https://thumbs.gfycat.com/FittingDizzyHornedviper-size_restricted.gif', 'http://bestanimations.com/Music/Dancers/anime-dancing-girls/anime-kawaii-cute-dance-animated-gif-image-5.gif', 'https://media.giphy.com/media/euMGM3uD3NHva/giphy.gif', 'https://thumbs.gfycat.com/PinkIllfatedClownanemonefish-small.gif', 'https://d2w9rnfcy7mm78.cloudfront.net/2145256/original_cd9c01187cead45cd791beafa78f7e08.gif?1525707539', 'https://media.giphy.com/media/oy8FiuwqTfWdW/giphy.gif', 'https://media.giphy.com/media/11lxCeKo6cHkJy/giphy.gif', 'https://i.pinimg.com/originals/4e/a6/b5/4ea6b5a95320003a13c03f09351abca0.gif', 'https://media.tenor.com/images/6c42f5b23210f512be5de188c0c024f1/tenor.gif', ]

        image = random.choice(choices)
        
        embed = discord.Embed(description=dance.format(author), colour=discord.Colour(0x644aba))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Dance(bot)
    bot.add_cog(n)
