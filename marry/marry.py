# coding=utf-8
import discord
from discord.ext import commands
import os
from .utils import checks
from __main__ import settings
from cogs.utils.dataIO import dataIO
import asyncio

#written by PlanetTeamSpeakk/PTSCogs https://github.com/PlanetTeamSpeakk/PTSCogs

#improved and rewritten by dimxxz https://github.com/dimxxz/dimxxz-Cogs

class Marry:
    """Marry your loved one."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/marry/settings.json")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    async def marry(self, ctx, yourlovedone:discord.Member):
        """Marry your loved one."""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {'marry_limit': 1, 'disabled': False}
            self.save_settings()
        if 'disabled' not in self.settings[ctx.message.server.id]:
            self.settings[ctx.message.server.id]['disabled'] = False
            self.save_settings()
        if not self.settings[ctx.message.server.id]['disabled']:
            if yourlovedone.id == ctx.message.author.id:
                msg = "You can't marry yourself, that would be weird wouldn't it?"
                e = discord.Embed(description=msg, colour=discord.Colour.red())
                await self.bot.say(embed=e)
                return
            elif yourlovedone.id == ctx.message.server.me.id:
                if ctx.message.author.id != settings.owner:
                    msg = "I'd only marry my owner."
                    e = discord.Embed(description=msg, colour=discord.Colour.red())
                    await self.bot.say(embed=e)
                    return
        else:
            await self.bot.say("Marriages are disabled in this server.")
            return
        times_married1 = 0
        times_married2 = 0
        for role in ctx.message.author.roles:
            if "❤" in role.name:
                if ctx.message.author.name in role.name:
                    if yourlovedone.name in role.name:
                        msg = "You're already married with this person."
                        e = discord.Embed(description=msg, colour=discord.Colour.red())
                        await self.bot.say(embed=e)
                        return
                    else:
                        pass
                times_married1 = times_married1 + 1
        if times_married1 >= self.settings[ctx.message.server.id]['marry_limit']:
            msg = "You have reached the marry limit ({}).".format(self.settings[ctx.message.server.id]['marry_limit'])
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return

        for role2 in yourlovedone.roles:
            if "❤" in role2.name:
                times_married2 = times_married2 + 1
        if times_married2 >= self.settings[ctx.message.server.id]['marry_limit']:
            msg = "Your loved one has reached the marry limit ({}).".format(self.settings[ctx.message.server.id]['marry_limit'])
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        await asyncio.sleep(1)

        msg = "**{}** do you take **{}** as your husband/wife? :ring: :heart: (yes/no)".format(yourlovedone.name, ctx.message.author.name)
        e = discord.Embed(title="Marriage:", description=msg, colour=discord.Colour.blue())
        await self.bot.say(yourlovedone.mention)
        await asyncio.sleep(1)
        await self.bot.say(embed=e)
        answer = await self.bot.wait_for_message(timeout=60, author=yourlovedone)
        if answer is None:
            msg = "The user you tried to marry didn't respond, I'm sorry."
            e = discord.Embed(description=msg, colour=discord.Colour.orange())
            await self.bot.say(embed=e)
            return
        elif not answer.content.lower().startswith('yes'):#"yes" not in answer.content.lower():
            msg = "The user you tried to marry didn't say **yes**, I'm sorry."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        try:
            married_role = await self.bot.create_role(server=ctx.message.server, name="{} ❤ {}".format(ctx.message.author.name, yourlovedone.name), colour=discord.Colour(value=0XfC8AF5)) #FF00EE))
        except discord.Forbidden:
            msg = "I do not have the `manage roles` permission, you can't marry until I do."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        except Exception as e:
            msg = "Couldn't make your loved role, unknown error occured,\n{}.".format(e)
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        await self.bot.add_roles(ctx.message.author, married_role)
        await self.bot.add_roles(yourlovedone, married_role)
        msg = "You married **{0}** in **{1}**\nYour divorce id is `{2}`, don't ever give this to anyone or they can divorce you!\nTo divorce type `{3}divorce {2}`.".format(str(yourlovedone), ctx.message.server.name, married_role.id, ctx.prefix)
        try:
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.send_message(ctx.message.author, embed = e)
        except:
            em = discord.Embed(description="Please turn on PM, **{}**!\nI can't DM you!".format(ctx.message.author.name), colour=discord.Colour.red())
            await self.bot.say(embed=em)
            await self.bot.delete_role(ctx.message.server, married_role)
            em = discord.Embed(description="Canceling marriage!".format(yourlovedone.name), colour=discord.Colour.red())
            await self.bot.say(embed=em)
            return

        if not yourlovedone.bot:
            msg = "You married **{0}** in **{1}**\nYour divorce id is `{2}`, don't ever give this to anyone or they can divorce you!\nTo divorce type `{3}divorce {2}`.".format(str(ctx.message.author), ctx.message.server.name, married_role.id, ctx.prefix)
            try:
                e = discord.Embed(description=msg, colour=discord.Colour.blue())
                await self.bot.send_message(yourlovedone, embed = e)
            except:
                em = discord.Embed(description="Please turn on PM, **{}**!\nI can't DM you!".format(yourlovedone.name), colour=discord.Colour.red())
                await self.bot.say(embed=em)
                await self.bot.delete_role(ctx.message.server, married_role)
                em = discord.Embed(description="Canceling marriage!".format(yourlovedone.name), colour=discord.Colour.red())
                await self.bot.say(embed=em)
                return
        else:
            pass
        marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
        if marchan:
            msg = "You're now married, congratulations!"
            msg2 = "**{}** married **{}** congratulations!".format(ctx.message.author.name, yourlovedone.name)
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            e2 = discord.Embed(description=msg2, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            await self.bot.send_message(marchan, embed=e2)
        else:
            try:
                marchan = await self.bot.create_channel(ctx.message.server, "marriage")
                msg = "You're now married, congratulations!"
                msg2 = "**{}** married **{}** congratulations!".format(ctx.message.author.name, yourlovedone.name)
                e = discord.Embed(description=msg, colour=discord.Colour.blue())
                e2 = discord.Embed(description=msg2, colour=discord.Colour.blue())
                await self.bot.say(embed=e)
                await self.bot.send_message(marchan, embed=e2)
            except:
                msg = "**{}** married **{}**, congratulations! I suggest telling the server owner or moderators to make a #marriage channel though.".format(ctx.message.author.name, yourlovedone.name)
                e = discord.Embed(description=msg, colour=discord.Colour.green())
                await self.bot.say(embed=e)
        return

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    async def marryit(self, ctx, thing):
        """Marry your loved things or non-user characters"""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {'marry_limit': 1, 'disabled': False}
            self.save_settings()
        if 'disabled' not in self.settings[ctx.message.server.id]:
            self.settings[ctx.message.server.id]['disabled'] = False
            self.save_settings()
        if not self.settings[ctx.message.server.id]['disabled']:
            if thing == ctx.message.author.id:
                msg = "You can't marry yourself, that would be weird wouldn't it?"
                e = discord.Embed(description=msg, colour=discord.Colour.red())
                await self.bot.say(embed=e)
                return
            elif thing == ctx.message.server.me.mention:
                if ctx.message.author.id != settings.owner:
                    msg = "I'd only marry my owner."
                    e = discord.Embed(description=msg, colour=discord.Colour.red())
                    await self.bot.say(embed=e)
                    return
        else:
            msg = "Marriages are disabled in this server."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        if thing.startswith("<@"):
            await self.bot.say("Nani? This command won't work with mentions or users. Please use **{}marry @user** instead!".format(ctx.prefix))
            return
        times_married = 0
        for role in ctx.message.author.roles:
            if "♡" in role.name:
                times_married = times_married + 1
        if times_married >= 2:
            msg = "You have reached the marry limit (2)."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        try:
            married_role = await self.bot.create_role(server=ctx.message.server, name="{} ♡ {}".format(ctx.message.author.name, thing), colour=discord.Colour(value=0XC05BF6)) #FF00EE))
        except discord.Forbidden:
            msg = "I do not have the `manage roles` permission, you can't marry until I do."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        except Exception as e:
            msg = "Couldn't make your loved role, unknown error occured,\n{}.".format(e)
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        await self.bot.add_roles(ctx.message.author, married_role)
        msg = "You married **{0}** in **{1}**\nYour divorce id is `{2}`, don't ever give this to anyone or they can divorce you!\nTo divorce type `{3}divorce {2}`.".format(str(thing), ctx.message.server.name, married_role.id, ctx.prefix)
        try:
            e = discord.Embed(description=msg, colour=discord.Colour.green())
            await self.bot.send_message(ctx.message.author, embed=e)
        except:
            em = discord.Embed(description="Please turn on PM, **{}**!\nI can't DM you!".format(ctx.messge.author.name), colour=discord.Colour.red())
            await self.bot.say(embed=em)
            await self.bot.delete_role(ctx.message.server, married_role)
            em = discord.Embed(description="Canceling marriage!".format(ctx.message.author.name), colour=discord.Colour.red())
            await self.bot.say(embed=em)
            return

        marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
        if marchan:
            msg = "You're now married to **{}**, congratulations!".format(thing)
            msg2 = "**{}** married **{}** congratulations!".format(ctx.message.author.name, thing)
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            e2 = discord.Embed(description=msg2, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            await self.bot.send_message(marchan, embed=e2)
        else:
            try:
                marchan = await self.bot.create_channel(ctx.message.server, "marriage")
                msg = "You're now married to **{}**, congratulations!".format(thing)
                msg2 = "**{}** married **{}** congratulations!".format(ctx.message.author.name, thing)
                e = discord.Embed(description=msg, colour=discord.Colour.blue())
                e2 = discord.Embed(description=msg2, colour=discord.Colour.blue())
                await self.bot.say(embed=e)
                await self.bot.send_message(marchan, embed=e2)
            except:
                msg = "**{}** married **{}**, congratulations! I suggest telling the server owner or moderators to make a #marriage channel though.".format(ctx.message.author.name, thing)
                e = discord.Embed(description=msg, colour=discord.Colour.blue())
                await self.bot.say(embed=e)
        return

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def forcemarry(self, ctx, person:discord.Member, lovedone:discord.Member):
        """Force marry 2 users."""
        if (ctx.message.server.id not in self.settings) or ("marry_limit" not in self.settings[ctx.message.server.id]):
            self.settings[ctx.message.server.id] = {'marry_limit': 0, 'disabled': False}
            self.save_settings()
        if 'disabled' not in self.settings[ctx.message.server.id]:
            self.settings[ctx.message.server.id]['disabled'] = False
            self.save_settings()
        if not self.settings[ctx.message.server.id]['disabled']:
            if lovedone.id == person.id:
                msg = "You can't let someone marry him/herself that would be weird wouldn't it?"
                e = discord.Embed(description=msg, colour=discord.Colour.blue())
                await self.bot.say(embed = e)
                return
            for role in person.roles:
                if person.name in role.name:
                    if "❤" in role.name:
                        if lovedone.name in role.name:
                            msg = "This person is already married with his/her loved one."
                            e = discord.Embed(description=msg, colour=discord.Colour.red())
                            await self.bot.say(embed=e)
                            return
            if lovedone.id == ctx.message.server.me.id:
                if ctx.message.author.id != settings.owner:
                    msg = "I will only marry my owner."
                    e = discord.Embed(description=msg, colour=discord.Colour.red())
                    await self.bot.say(embed=e)
                    return
            elif person.id == ctx.message.server.me.id:
                if ctx.message.author.id != settings.owner:
                    msg = "I will only marry my owner."
                    e = discord.Embed(description=msg, colour=discord.Colour.red())
                    await self.bot.say(embed=e)
                    return
        else:
            msg = "Marriages are disabled in this server."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        times_married1 = 0
        times_married2 = 0
        for role in person.roles:
            if "❤" in role.name:
                times_married1 = times_married1 + 1

        if times_married1 >= self.settings[ctx.message.server.id]['marry_limit']:
            msg = "**{}** has reached the marry limit (**{}**).".format(person.name, self.settings[ctx.message.server.id]['marry_limit'])
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        for rolev in lovedone.roles:
            if "❤" in rolev.name:
                times_married2 = times_married2 + 1
            if times_married2 >= self.settings[ctx.message.server.id]['marry_limit']:
                msg = "**{}** has reached the marry limit (**{}**).".format(lovedone.name, self.settings[ctx.message.server.id]['marry_limit'])
                e = discord.Embed(description=msg, colour=discord.Colour.red())
                await self.bot.say(embed=e)
                return
        try:
            married_role = await self.bot.create_role(server=ctx.message.server, name="{} ❤ {}".format(person.name, lovedone.name), colour=discord.Colour(value=0XF84444)) #FF00EE))
        except discord.Forbidden:
            msg = "I do not have the `manage roles` permission, you can't marry until I do."
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            return
        except Exception as e:
            msg = "Couldn't make your loved role, unknown error occured,\n{}.".format(e)
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        await self.bot.add_roles(person, married_role)
        await self.bot.add_roles(lovedone, married_role)
        try:
            msg = "**{0}** married you to **{1}** in **{2}**.\nYour divorce id is `{3}`, don't ever give this to anyone or they can divorce you!\nTo divorce type `{4}divorce {3}`.".format(ctx.message.author.name, str(lovedone), ctx.message.server.name, married_role.id, ctx.prefix)
            e = discord.Embed(description=msg, colour=discord.Colour.green())
            await self.bot.send_message(person, embed = e)
        except:
            pass
        try:
            msg = "**{0}** married you to **{1}** in **{2}**.\nYour divorce id is `{3}`, don't ever give this to anyone or they can divorce you!\nTo divorce type `{4}divorce {3}`.".format(ctx.message.author.name, str(person), ctx.message.server.name, married_role.id, ctx.prefix)
            e = discord.Embed(description=msg, colour=discord.Colour.green())
            await self.bot.send_message(lovedone, embed=e)
        except:
            pass
        else:
            pass
        marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
        if marchan:
            msg = "They're now married, congratulations!"
            msg2 = "{} was forced to marry {}.".format(person.mention, lovedone.mention)
            e = discord.Embed(description=msg, colour=discord.Colour.orange())
            e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
            await self.bot.say(embed=e)
            await self.bot.send_message(marchan, embed = e2)
        else:
            try:
                marchan = await self.bot.create_channel(ctx.message.server, "marriage")
                msg = "They're now married, congratulations!"
                msg2 = "{} was forced to marry {}.".format(person.mention, lovedone.mention)
                e = discord.Embed(description=msg, colour=discord.Colour.orange())
                e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
                await self.bot.say(embed=e)
                await self.bot.send_message(marchan, embed = e2)
            except:
                msg = "{} married {}, congratulations! I suggest telling the server owner or moderators to make a #marriage channel though.".format(person.mention, lovedone.mention)
                e = discord.Embed(description=msg, colour=discord.Colour.green())
                await self.bot.say(embed = e)
                return
        
    @commands.command(pass_context=True, no_pm=True)
    async def divorce(self, ctx, divorce_id):
        """Divorce your ex."""
        try:
            married_role = discord.utils.get(ctx.message.server.roles, id=divorce_id)
            await self.bot.delete_role(ctx.message.server, married_role)
            marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
            if marchan:
                msg = "You're now divorced."
                msg2 = "{} divorced ID `{}`.".format(ctx.message.author.mention, divorce_id)
                e = discord.Embed(description=msg, colour=discord.Colour.orange())
                e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
                await self.bot.say(embed=e)
                await self.bot.send_message(marchan, embed=e2)
            else:
                try:
                    marchan = await self.bot.create_channel(ctx.message.server, "marriage")
                    msg = "You're now divorced."
                    msg2 = "{} divorced ID `{}`.".format(ctx.message.author.mention, divorce_id)
                    e = discord.Embed(description=msg, colour=discord.Colour.orange())
                    e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
                    await self.bot.say(embed=e)
                    await self.bot.send_message(marchan, embed=e2)
                except:
                    msg = "You're now divorced! I suggest telling the server owner or moderators to make a #marriage channel though."
                    e = discord.Embed(description=msg, colour=discord.Colour.red())
                    await self.bot.say(embed=e)
                    return
        except discord.Forbidden:
            msg = "I do not have the `manage roles` permission, I need it to divorce you."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return
        except:
            msg = "That's not a valid ID."
            e = discord.Embed(description=msg, colour=discord.Colour.red())
            await self.bot.say(embed=e)
            return

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def setmarrylimit(self, ctx, times:int):
        """Sets the limit someone can marry someone. 0 is unlimited."""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {}
        self.settings[ctx.message.server.id]['marry_limit'] = times
        self.save_settings()
        msg = "Done!"
        e = discord.Embed(description=msg, colour=discord.Colour.blue())
        await self.bot.say(embed=e)
       
    @commands.command(pass_context=True, no_pm=True)
    async def marrylimit(self, ctx):
        """Shows you the current marrylimit."""
        self.settings = dataIO.load_json("data/marry/settings.json")
        if (ctx.message.server.id not in self.settings) or ("marry_limit" not in self.settings[ctx.message.server.id]):
            msg = "There is no marry limit."
            e = discord.Embed(description=msg, colour=discord.Colour.orange())
            await self.bot.say(embed=e)
        elif self.settings[ctx.message.server.id]['marry_limit'] == 0:
            msg = "There is no marry limit."
            e = discord.Embed(description=msg, colour=discord.Colour.orange())
            await self.bot.say(embed=e)
        else:
            msg = "The marry limit is {}.".format(self.settings[ctx.message.server.id]['marry_limit'])
            e = discord.Embed(description=msg, colour=discord.Colour.orange())
            await self.bot.say(embed=e)
        
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def massdivorce(self, ctx):
        """Divorces everyone on the server."""
        msg = "Are you sure you want to divorce everyone on the server? (yes/no)"
        e = discord.Embed(description=msg, colour=discord.Colour.blue())
        await self.bot.say(embed=e)
        answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)
        if answer is None:
            msg = "Ok, then not."
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            return
        elif "yes" in answer.content.lower():
            divorced = 0
            for role in ctx.message.server.roles:
                if "❤" in role.name:
                    try:
                        await self.bot.delete_role(role=role, server=ctx.message.server)
                        divorced = divorced + 1
                    except:
                        pass
                elif "♡" in role.name:
                    try:
                        await self.bot.delete_role(role=role, server=ctx.message.server)
                        divorced = divorced + 1
                    except:
                        pass
            marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
            if marchan:
                msg = "Done! Divorced **{}** couples.".format(divorced)
                msg2 = "**{}** divorced everyone (**{}** couples).".format(ctx.message.author.name, divorced)
                e = discord.Embed(description=msg, colour=discord.Colour.orange())
                e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
                await self.bot.say(embed=e)
                await self.bot.send_message(marchan, embed=e2)
            else:
                try:
                    marchan = await self.bot.create_channel(ctx.message.server, "marriage")
                    msg = "Done! Divorced **{}** couples.".format(divorced)
                    msg2 = "**{}** divorced everyone (**{}** couples).".format(ctx.message.author.name, divorced)
                    e = discord.Embed(description=msg, colour=discord.Colour.orange())
                    e2 = discord.Embed(description=msg2, colour=discord.Colour.orange())
                    await self.bot.say(embed=e)
                    await self.bot.send_message(marchan, embed=e2)
                except:
                    msg = "Done! Everyone has been divorced. I suggest telling the server owner or moderators to make a #marriage channel though."
                    e = discord.Embed(description=msg, colour=discord.Colour.orange())
                    await self.bot.say(embed=e)
                    return
            self.settings[ctx.message.server.id] = {'marry_limit': 1, 'disabled': False}
            self.save_settings()
        else:
            msg = "K then not."
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            return
            
    @commands.command(pass_context=True, no_pm=True)
    async def marrycount(self, ctx):
        """Counts all the married couples in this server."""
        count = 0
        for role in ctx.message.server.roles:
            if " ❤ " in role.name:
                count += 1
        if count == 1:
            msg = "There is currently {} married couple in this server.".format(count)
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
        else:
            msg = "There are currently {} married couples in this server.".format(count)
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
            
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def admindivorce(self, ctx, person:discord.Member, lovedone:discord.Member):
        """Divorces someone by NAME. If the name is bigger than one word put quotes around it
        Example: "much name, such words"."""
        personx = person.id
        personx2 = lovedone.id
        for role in ctx.message.server.roles:
            if person.name in role.name:
                if " ❤ " in role.name:
                    if lovedone.name in role.name:
                        try:
                            await self.bot.delete_role(ctx.message.server, role)
                            marchan = discord.utils.find(lambda c: c.name == 'marriage', ctx.message.server.channels)
                            if marchan:
                                msg = "{} admindivorced {} and {}.".format(ctx.message.author.name, person.name, lovedone.name)
                                e = discord.Embed(description=msg, colour=discord.Colour.orange())
                                await self.bot.send_message(marchan, embed=e)
                            else:
                                marchan = self.bot.create_channel(ctx.message.server, "marriage")
                                msg = "{} admindivorced {} and {}.".format(ctx.message.author.name, person.name, lovedone.name)
                                e = discord.Embed(description=msg, colour=discord.Colour.orange())
                                await self.bot.send_message(marchan, embed=e)
                            msg = "Succesfully divorced {} and {}.".format(person.name, lovedone.name)
                            e = discord.Embed(description=msg, colour=discord.Colour.orange())
                            await self.bot.say(embed=e)
                            return
                        except:
                            msg = "The role for the marriage was found but could not be deleted."
                            e = discord.Embed(description=msg, colour=discord.Colour.red())
                            await self.bot.say(embed=e)
                            return
        msg = "The role of that marriage could not be found."
        e = discord.Embed(description=msg, colour=discord.Colour.red())
        await self.bot.say(embed=e)
        
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def togglemarriage(self, ctx):
        """Toggles if members of your server should be able to marry each other using [p]marry."""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {'marrylimit': 0, 'disabled': False}
        if not self.settings[ctx.message.server.id]['disabled']:
            self.settings[ctx.message.server.id]['disabled'] = True
            msg = "Members can no longer marry each other anymore."
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
        else:
            self.settings[ctx.message.server.id]['disabled'] = False
            msg = "Members can once again marry each other."
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            await self.bot.say(embed=e)
        self.save_settings()


    def save_settings(self):
        dataIO.save_json("data/marry/settings.json", self.settings)
        
def check_folders():
    if not os.path.exists("data/marry"):
        print("Creating data/marry folder...")
        os.makedirs("data/marry")
    if not os.path.exists("data/marry/images"):
        print("Creating data/marry/images folder...")
        os.makedirs("data/marry/images")
        
def check_files():
    if not os.path.exists("data/marry/settings.json"):
        print("Creating data/marry/settings.json file...")
        dataIO.save_json("data/marry/settings.json", {})
        
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Marry(bot))
