from discord.ext import commands
import random
import discord

class highfiveplus:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def highfive(self, context, member: discord.Member):
        """Give someone a highfive with a gif :)"""
        author = context.message.author.mention
        mention = member.mention
        
        hug = "**{0} gave {1} a highfive!**"
        
        choices = ['https://i.gifer.com/B0aW.gif', 'http://gifimage.net/wp-content/uploads/2017/09/anime-high-five-gif.gif', 'https://i.gifer.com/QEIo.gif', 'https://78.media.tumblr.com/85b0f366d1c596a7e54ea1496f303ae6/tumblr_nqcba47l1Q1qdl4hco4_500.gif', 'https://i.pinimg.com/originals/fc/b1/44/fcb1446b74166b0860ace50ed8b33686.gif', 'https://data.whicdn.com/images/216194566/original.gif', 'http://1.bp.blogspot.com/-lXQRidJkUSc/UfpI5ZG81_I/AAAAAAAAB_0/MHw4jp6-REU/s1600/high+five.gif', 'https://66.media.tumblr.com/a125f8c7b6de525c56baf9c459e13fba/tumblr_oi4wa3eXNB1vjcm8po1_400.gif', 'https://i.gifer.com/DX1i.gif', 'http://fanaru.com/no-game-no-life/image/185767-no-game-no-life-high-five.gif', 'https://thumbs.gfycat.com/WellmadeSlowIguanodon-small.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-high-five-gif-12.gif', 'https://vignette.wikia.nocookie.net/animal-jam-clans-1/images/c/cd/88635-fairy-tail-high-five.gif/revision/latest?cb=20170109030956', 'http://4.bp.blogspot.com/-zFgKJCMQY0s/VCh7Q7B6NCI/AAAAAAAAUbQ/RQu02-605Uw/s1600/Futs%C5%AB%2Bno%2BJoshik%C5%8Dsei%2Bga%2BLocodol%2BYattemita2.gif', 'https://66.media.tumblr.com/d43f65f354b381f041b20df5a1bc9066/tumblr_inline_o280458pPM1tdmtiy_500.gif', 'http://i.imgur.com/Z99zi6m.gif', 'https://1.bp.blogspot.com/-zCYOY8ef-Ro/WfUW-iO8Y5I/AAAAAAAA-MM/uQYRw57PmYM_pjl8kJQDAs1EKLB_-2CKgCKgBGAs/s1600/Omake+Gif+Anime+-+Love+Live%2521+Sunshine%2521%2521+S2+-+Episode+4+-+Yoshiko+Mari+High+Five.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-high-five-gif-10.gif', 'http://1.bp.blogspot.com/-lXQRidJkUSc/UfpI5ZG81_I/AAAAAAAAB_0/MHw4jp6-REU/s1600/high+five.gif', 'https://i.imgur.com/rvBVoey.gif', 'https://i.kym-cdn.com/photos/images/original/001/126/190/908.gif', 'https://thumbs.gfycat.com/BreakableMessyHarrierhawk-size_restricted.gif', 'https://i.kym-cdn.com/photos/images/original/001/125/001/7c5.gif', 'https://i.gifer.com/Pvwh.gif', 'https://i.gifer.com/B0aW.gif', 'https://media.giphy.com/media/KNGlioVGvwBXO/giphy.gif', 'https://media.giphy.com/media/x58AS8I9DBRgA/giphy.gif', 'https://media1.tenor.com/images/7b1f06eac73c36721912edcaacddf666/tenor.gif']
        
        image = random.choice(choices)
        
        embed = discord.Embed(description=hug.format(author, mention), colour=discord.Colour(0xba4b5b))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = highfiveplus(bot)
    bot.add_cog(n)
