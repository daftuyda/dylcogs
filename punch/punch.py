from discord.ext import commands
import random
import discord

class Punch:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def punch(self, context, member: discord.Member):
        """Punch thy enemy!"""
        author = context.message.author.mention
        mention = member.mention
        
        punch = "**{0} punched {1}!**"
        
        choices = ['https://media1.tenor.com/images/2efcac044a4f9f2377b118b1cc6282cb/tenor.gif', 'https://i.kym-cdn.com/photos/images/original/001/135/370/d3f.gif', 'https://discourse-cdn-sjc1.com/business5/uploads/wanikani_community/original/3X/6/5/655f5f0e15fcc78bd865a4476813ee082fde2405.gif', 'https://pa1.narvii.com/6287/531da1049bc01a84aeb995082ade903c3ea431bf_hq.gif', 'https://vignette.wikia.nocookie.net/pripara-idol-academy/images/c/c0/B50.gif', 'https://i.gifer.com/Ua1c.gif', 'https://thumbs.gfycat.com/NewDearFulmar-small.gif', 'https://media1.tenor.com/images/0e4dc717bb99433c6ef3089f418dc94a/tenor.gif', 'https://i.kym-cdn.com/photos/images/original/000/971/995/71e.gif', 'https://media.giphy.com/media/zA1WmSCdUgxri/giphy.gif', 'https://i.imgur.com/BhvWwuS.gif', 'https://i.gifer.com/1Ky5.gif', 'https://i.imgur.com/uni3hdF.gif', 'https://thumbs.gfycat.com/BitesizedEnragedAfricanaugurbuzzard-size_restricted.gif', 'https://pa1.narvii.com/5668/d845ea44f1ce209351976f2a22b4c728873fac21_hq.gif', 'https://media.giphy.com/media/GIZICC6rFPgzK/giphy.gif', 'https://i.gifer.com/VuLl.gif', 'https://cdn172.picsart.com/222035215014201.gif', 'https://gifimage.net/wp-content/uploads/2017/09/anime-punch-gif-9.gif', 'http://67.media.tumblr.com/7d58e35bef43e61530296224e619695f/tumblr_ogk36k1tT71son3fpo2_500.gif', 'https://i.imgur.com/g91XPGA.gif', 'https://thumbs.gfycat.com/SecondFeminineDuckbillcat-size_restricted.gif', 'https://thumbs.gfycat.com/IllinformedRipeFlounder-small.gif', 'https://media.giphy.com/media/iWAqMe8hBWKVq/giphy-downsized-large.gif', 'https://media.giphy.com/media/YjHx1taZwpfd6/giphy.gif', 'https://media.tenor.com/images/b561ad7377142adf365fe33f20fa45e8/tenor.gif', ]
        image = random.choice(choices)
        
        embed = discord.Embed(description=punch.format(author, mention), colour=discord.Colour(0x644aba))
        embed.set_image(url=image)

        await self.bot.say(embed=embed)

def setup(bot):
    n = Punch(bot)
    bot.add_cog(n)
