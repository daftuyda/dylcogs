import discord
from discord.ext import commands
from discord.utils import find
from .utils.chat_formatting import pagify
from __main__ import send_cmd_help
import platform, asyncio, string, operator, random, textwrap
import os, re, aiohttp
import math
from .utils.dataIO import fileIO
from cogs.utils import checks
try:
    import pymongo
    from pymongo import MongoClient
except:
    raise RuntimeError("Can't load pymongo. Do 'pip3 install pymongo'.")
try:
    import scipy
    import scipy.misc
    import scipy.cluster
except:
    pass
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps, ImageFilter
except:
    raise RuntimeError("Can't load pillow. Do 'pip3 install pillow'.")
import time

__author__ = "stevy"
# written by stevy https://github.com/AznStevy/Maybe-Useful-Cogs
# Modified by dimxxz https://github.com/dimxxz/dimxxz-Cogs

# fonts
font_file = 'data/leveler/fonts/font.ttf'
font_bold_file = 'data/leveler/fonts/font_bold.ttf'
font_unicode_file = 'data/leveler/fonts/unicode.ttf'

# Credits (None)
bg_credits = {

}

# directory
user_directory = "data/leveler/users"

pref = fileIO("data/red/settings.json", "load")#['PREFIXES']
prefix = pref['PREFIXES']
default_avatar_url = "http://i.imgur.com/XPDO9VH.jpg"

try:
    client = MongoClient()
    db = client['leveler']
except:
    print("Can't load database. Follow instructions on Git/online to install MongoDB.")

class Leveler:
    """A level up thing with image generation!"""

    def __init__(self, bot):
        self.bot = bot
        #self.backgrounds = fileIO("data/leveler/backgrounds.json", "load")
        self.badges = fileIO("data/leveler/badges.json", "load")
        self.settings = fileIO("data/leveler/settings.json", "load")
        bot_settings = fileIO("data/red/settings.json", "load")
        self.owner = bot_settings["OWNER"]
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.chid = fileIO("data/leveler/channels.json", "load")

        dbs = client.database_names()
        if 'leveler' not in dbs:
            self.pop_database()

    def __unload(self):
        self.session.close()

    def pop_database(self):
        if os.path.exists("data/leveler/users"):
            for userid in os.listdir(user_directory):
                userinfo = fileIO("data/leveler/users/{}/info.json".format(userid), "load")
                userinfo['user_id'] = userid
                db.users.insert_one(userinfo)

    def create_global(self):

                userinfo = fileIO("data/leveler/users/{}/info.json".format(userid), "load")
                userinfo['user_id'] = userid
                db.users.insert_one(userinfo)


    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name = "profile", pass_context=True, no_pm=True)
    async def profile(self,ctx, *, user : discord.Member=None):
        """Displays a user profile."""
        if user == None:
            user = ctx.message.author
        channel = ctx.message.channel
        server = user.server
        curr_time = time.time()

        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        # check if disabled
        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        # no cooldown for text only
        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            em = await self.profile_text(user, server, userinfo)
            await self.bot.send_message(channel, '', embed = em)
        else:
            await self.draw_profile(user, server)
            await self.bot.send_typing(channel)
            try:
                await self.bot.send_file(channel, 'data/leveler/temp/{}_profile.png'.format(user.id), content='**User profile for {}**'.format(self._is_mention(user)))
            except:
                return
            db.users.update_one({'user_id':user.id}, {'$set':{
                    "profile_block": curr_time,
                }}, upsert = True)

            os.remove('data/leveler/temp/{}_profile.png'.format(user.id))


    async def profile_text(self, user, server, userinfo):
        def test_empty(text):
            if text == '':
                return "None"
            else:
                return text

        em = discord.Embed(description='', colour=user.colour)
        em.add_field(name="Title:", value = test_empty(userinfo["title"]))
        em.add_field(name="Reps:", value= userinfo["rep"])
        em.add_field(name="Global Rank:", value = '#{}'.format(await self._find_global_rank(user)))
        em.add_field(name="Server Rank:", value = '#{}'.format(await self._find_server_rank(user, server)))
        em.add_field(name="Server Level:", value = format(userinfo["servers"][server.id]["level"]))
        em.add_field(name="Total Exp:", value = userinfo["total_exp"])
        em.add_field(name="Server Exp:", value = await self._find_server_exp(user, server))
        try:
            bank = self.bot.get_cog('Economy').bank
            if bank.account_exists(user):
                credits = bank.get_balance(user)
            else:
                credits = 0
        except:
            credits = 0
        em.add_field(name="Credits: ", value = "${}".format(credits))
        em.add_field(name="Info: ", value = test_empty(userinfo["info"]))
        em.add_field(name="Badges: ", value = test_empty(", ".join(userinfo["badges"])).replace("_", " "))
        em.set_author(name="Profile for {}".format(user.name), url = user.avatar_url)
        em.set_thumbnail(url=user.avatar_url)
        return em

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    async def rank(self,ctx,user : discord.Member=None):
        """Displays the rank of a user."""
        if user == None:
            user = ctx.message.author
        channel = ctx.message.channel
        server = user.server
        curr_time = time.time()

        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        # check if disabled
        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        # no cooldown for text only
        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            em = await self.rank_text(user, server, userinfo)
            await self.bot.send_message(channel, '', embed = em)
        else:
            await self.draw_rank(user, server)
            await self.bot.send_typing(channel)
            try:
                await self.bot.send_file(channel, 'data/leveler/temp/{}_rank.png'.format(user.id), content='**Ranking & Statistics for {}**'.format(self._is_mention(user)))
            except:
                return
            db.users.update_one({'user_id':user.id}, {'$set':{
                    "rank_block".format(server.id): curr_time,
                }}, upsert = True)

            os.remove('data/leveler/temp/{}_rank.png'.format(user.id))


    async def rank_text(self, user, server, userinfo):
        em = discord.Embed(description='', colour=user.colour)
        em.add_field(name="Server Rank", value = '#{}'.format(await self._find_server_rank(user, server)))
        em.add_field(name="Reps", value = userinfo["rep"])
        em.add_field(name="Server Level", value = userinfo["servers"][server.id]["level"])
        em.add_field(name="Server Exp", value = await self._find_server_exp(user, server))
        em.set_author(name="Rank and Statistics for {}".format(user.name), url = user.avatar_url)
        em.set_thumbnail(url=user.avatar_url)
        return em

    # should the user be mentioned based on settings?
    def _is_mention(self,user):
        if "mention" not in self.settings.keys() or self.settings["mention"]:
            return user.mention
        else:
            return user.name

    # @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    async def top(self, ctx, *options):
        '''Displays leaderboard. Add "global" parameter for global'''
        server = ctx.message.server
        user = ctx.message.author

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        users = []
        board_type = ''
        user_stat = None
        if '-rep' in options and '-global' in options:
            title = "Global Rep Leaderboard for {}\n".format(self.bot.user.name)
            for userinfo in db.users.find({}):
                try:
                    users.append((userinfo["username"], userinfo["rep"]))
                except:
                    users.append((userinfo["user_id"], userinfo["rep"]))

                if user.id == userinfo["user_id"]:
                    user_stat = userinfo["rep"]

            board_type = 'Rep'
            footer_text = "Your Rank: {}         {}: {}".format(
                await self._find_global_rep_rank(user), board_type, user_stat)
            icon_url = self.bot.user.avatar_url
        elif '-global' in options:
            title = "Global Exp Leaderboard for {}\n".format(self.bot.user.name)
            for userinfo in db.users.find({}):
                try:
                    users.append((userinfo["username"], userinfo["total_exp"]))
                except:
                    users.append((userinfo["user_id"], userinfo["total_exp"]))

                if user.id == userinfo["user_id"]:
                    user_stat = userinfo["total_exp"]

            board_type = 'Points'
            footer_text = "Your Rank: {}         {}: {}".format(
                await self._find_global_rank(user), board_type, user_stat)
            icon_url = self.bot.user.avatar_url
        elif '-rep' in options:
            title = "Rep Leaderboard for {}\n".format(server.name)
            for userinfo in db.users.find({}):
                userid = userinfo["user_id"]
                if "servers" in userinfo and server.id in userinfo["servers"]:
                    target = discord.utils.get(self.bot.get_all_members(), id=userid)
                    if target in server.members:
                        try:
                            users.append((userinfo["username"], userinfo["rep"]))
                        except:
                            users.append((userinfo["user_id"], userinfo["rep"]))

                if user.id == userinfo["user_id"]:
                    user_stat = userinfo["rep"]

            board_type = 'Rep'
            print(await self._find_server_rep_rank(user, server))
            footer_text = "Your Rank: {}         {}: {}".format(
                await self._find_server_rep_rank(user, server), board_type, user_stat)
            icon_url = server.icon_url
        else:
            title = "Exp Leaderboard for {}\n".format(server.name)
            for userinfo in db.users.find({}):
                try:
                    userid = userinfo["user_id"]
                    if "servers" in userinfo and server.id in userinfo["servers"]:
                        server_exp = 0
                        for i in range(userinfo["servers"][server.id]["level"]):
                            server_exp += self._required_exp(i)
                        server_exp +=  userinfo["servers"][server.id]["current_exp"]
                        target = discord.utils.get(self.bot.get_all_members(), id=userid)
                        if target in server.members:
                            try:
                                users.append((userinfo["username"], server_exp))
                            except:
                                users.append((userinfo["user_id"], server_exp))
                except:
                    pass
            board_type = 'Points'
            footer_text = "Your Rank: {}         {}: {}".format(
                await self._find_server_rank(user, server), board_type,
                await self._find_server_exp(user, server))
            icon_url = server.icon_url
        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)

        # multiple page support
        page = 1
        per_page = 15
        pages = math.ceil(len(sorted_list)/per_page)
        for option in options:
            if str(option).isdigit():
                if page >= 1 and int(option) <= pages:
                    page = int(str(option))
                else:
                    await self.bot.say("**Please enter a valid page number! (1 - {})**".format(str(pages)))
                    return
                break

        msg = ""
        msg += "**Rank              Name (Page {}/{})**\n".format(page, pages)
        rank = 1 + per_page*(page-1)
        start_index = per_page*page - per_page
        end_index = per_page*page

        default_label = "   "
        special_labels = ["♔", "♕", "♖", "♗", "♘", "♙"]

        for single_user in sorted_list[start_index:end_index]:
            if rank-1 < len(special_labels):
                label = special_labels[rank-1]
            else:
                label = default_label

            msg += u'`{:<2}{:<2}{:<2}   # {:<22}'.format(rank, label, u"➤", self._truncate_text(single_user[0],20))
            msg += u'{:>5}{:<2}{:<2}{:<5}`\n'.format(" ", " ", " ", "Total {}: ".format(board_type) + str(single_user[1]))
            rank += 1
        msg +="----------------------------------------------------\n"
        msg += "`{}`".format(footer_text)

        em = discord.Embed(description='', colour=user.colour)
        em.set_author(name=title, icon_url = icon_url)
        em.description = msg

        await self.bot.say(embed = em)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(pass_context=True, no_pm=True)
    async def rep(self, ctx, user : discord.Member = None):
        """Gives a reputation point to a designated player."""
        channel = ctx.message.channel
        org_user = ctx.message.author
        server = org_user.server
        # creates user if doesn't exist
        await self._create_user(org_user, server)
        if user:
            await self._create_user(user, server)
        org_userinfo = db.users.find_one({'user_id':org_user.id})
        curr_time = time.time()

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return
        if user and user.id == org_user.id:
            await self.bot.say("**You can't give a rep to yourself!**")
            return
        if user and user.bot:
            await self.bot.say("**You can't give a rep to a bot!**")
            return
        if "rep_block" not in org_userinfo:
            org_userinfo["rep_block"] = 0

        delta = float(curr_time) - float(org_userinfo["rep_block"])
        if user and delta >= 43200.0 and delta>0:
            userinfo = db.users.find_one({'user_id':user.id})
            db.users.update_one({'user_id':org_user.id}, {'$set':{
                    "rep_block": curr_time,
                }})
            db.users.update_one({'user_id':user.id}, {'$set':{
                    "rep":  userinfo["rep"] + 1,
                }})
            await self.bot.say("**You have just given {} a reputation point!**".format(self._is_mention(user)))
        else:
            # calulate time left
            seconds = 43200 - delta
            if seconds < 0:
                await self.bot.say("**You can give a rep!**")
                return

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            await self.bot.say("**You need to wait {} hours, {} minutes, and {} seconds until you can give reputation again!**".format(int(h), int(m), int(s)))

    @commands.command(pass_context=True, no_pm=True)
    async def lvlinfo(self, ctx, user : discord.Member = None):
        """Gives more specific details about user profile image."""

        if not user:
            user = ctx.message.author
        server = ctx.message.server
        userinfo = db.users.find_one({'user_id':user.id})

        server = ctx.message.server

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        # creates user if doesn't exist
        await self._create_user(user, server)
        msg = ""
        msg += "Name: {}\n".format(user.name)
        msg += "Title: {}\n".format(userinfo["title"])
        msg += "Reps: {}\n".format(userinfo["rep"])
        msg += "Server Level: {}\n".format(userinfo["servers"][server.id]["level"])
        total_server_exp = 0
        for i in range(userinfo["servers"][server.id]["level"]):
            total_server_exp += self._required_exp(i)
        total_server_exp += userinfo["servers"][server.id]["current_exp"]
        msg += "Server Exp: {}\n".format(total_server_exp)
        msg += "Total Exp: {}\n".format(userinfo["total_exp"])
        msg += "Info: {}\n".format(userinfo["info"])
        msg += "Profile background: {}\n".format(userinfo["profile_background"])
        msg += "Rank background: {}\n".format(userinfo["rank_background"])
        msg += "Levelup background: {}\n".format(userinfo["levelup_background"])
        if "profile_info_color" in userinfo.keys() and userinfo["profile_info_color"]:
            msg += "Profile info color: {}\n".format(self._rgb_to_hex(userinfo["profile_info_color"]))
        if "profile_exp_color" in userinfo.keys() and userinfo["profile_exp_color"]:
            msg += "Profile exp color: {}\n".format(self._rgb_to_hex(userinfo["profile_exp_color"]))
        if "rep_color" in userinfo.keys() and userinfo["rep_color"]:
            msg += "Rep section color: {}\n".format(self._rgb_to_hex(userinfo["rep_color"]))
        if "badge_col_color" in userinfo.keys() and userinfo["badge_col_color"]:
            msg += "Badge section color: {}\n".format(self._rgb_to_hex(userinfo["badge_col_color"]))
        if "rank_info_color" in userinfo.keys() and userinfo["rank_info_color"]:
            msg += "Rank info color: {}\n".format(self._rgb_to_hex(userinfo["rank_info_color"]))
        if "rank_exp_color" in userinfo.keys() and userinfo["rank_exp_color"]:
            msg += "Rank exp color: {}\n".format(self._rgb_to_hex(userinfo["rank_exp_color"]))
        if "levelup_info_color" in userinfo.keys() and userinfo["levelup_info_color"]:
            msg += "Level info color: {}\n".format(self._rgb_to_hex(userinfo["levelup_info_color"]))
        msg += "Badges: "
        msg += ", ".join(userinfo["badges"])

        em = discord.Embed(description=msg, colour=user.colour)
        em.set_author(name="Profile Information for {}".format(user.name), icon_url = user.avatar_url)
        await self.bot.say(embed = em)

    def _rgb_to_hex(self, rgb):
        rgb = tuple(rgb[:3])
        return '#%02x%02x%02x' % rgb

    @commands.group(name = "lvlset", pass_context=True)
    async def lvlset(self, ctx):
        """Profile Configuration Options"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @lvlset.group(name = "profile", pass_context=True)
    async def profileset(self, ctx):
        """Profile options"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @lvlset.group(name = "rank", pass_context=True)
    async def rankset(self, ctx):
        """Rank options"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @lvlset.group(name = "levelup", pass_context=True)
    async def levelupset(self, ctx):
        """Level-Up options"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @profileset.command(name = "color", pass_context=True, no_pm=True)
    async def profilecolors(self, ctx, section:str, color:str):
        """Set info color. e.g [p]lvlset profile color [exp|rep|badge|info|all] [default|white|hex|auto]"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        section = section.lower()
        default_info_color = (30, 30 ,30, 200)
        white_info_color = (255, 255, 255, 255)
        default_rep = (92,130,203,230)
        default_badge = (128,151,165,230)
        default_exp = (255, 255, 255, 230)
        default_a = 200

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("**Text-only commands allowed.**")
            return

        # get correct section for db query
        if section == "rep":
            section_name = "rep_color"
        elif section == "exp":
            section_name = "profile_exp_color"
        elif section == "badge":
            section_name = "badge_col_color"
        elif section == "info":
            section_name = "profile_info_color"
        elif section == "all":
            section_name = "all"
        else:
            await self.bot.say("**Not a valid section. (rep, exp, badge, info, all)**")
            return

        # get correct color choice
        if color == "auto":
            if section == "exp":
                color_ranks = [random.randint(2,3)]
            elif section == "rep":
                color_ranks = [random.randint(2,3)]
            elif section == "badge":
                color_ranks = [0] # most prominent color
            elif section == "info":
                color_ranks = [random.randint(0,1)]
            elif section == "all":
                color_ranks = [random.randint(2,3), random.randint(2,3), 0, random.randint(0,2)]

            hex_colors = await self._auto_color(userinfo["profile_background"], color_ranks)
            set_color = []
            for hex_color in hex_colors:
                color_temp = self._hex_to_rgb(hex_color, default_a)
                set_color.append(color_temp)

        elif color == "white":
            set_color = [white_info_color]
        elif color == "default":
            if section == "exp":
                set_color = [default_exp]
            elif section == "rep":
                set_color = [default_rep]
            elif section == "badge":
                set_color = [default_badge]
            elif section == "info":
                set_color = [default_info_color]
            elif section == "all":
                set_color = [default_exp, default_rep, default_badge, default_info_color]
        elif self._is_hex(color):
            set_color = [self._hex_to_rgb(color, default_a)]
        else:
            await self.bot.say("**Not a valid color. (default, hex, white, auto)**")
            return

        if section == "all":
            if len(set_color) == 1:
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "profile_exp_color": set_color[0],
                        "rep_color": set_color[0],
                        "badge_col_color": set_color[0],
                        "profile_info_color": set_color[0]
                    }})
            elif color == "default":
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "profile_exp_color": default_exp,
                        "rep_color": default_rep,
                        "badge_col_color": default_badge,
                        "profile_info_color": default_info_color
                    }})
            elif color == "auto":
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "profile_exp_color": set_color[0],
                        "rep_color": set_color[1],
                        "badge_col_color": set_color[2],
                        "profile_info_color": set_color[3]
                    }})
            await self.bot.say("**Colors for profile set.**")
        else:
            print("update one")
            db.users.update_one({'user_id':user.id}, {'$set':{
                    section_name: set_color[0]
                }})
            await self.bot.say("**Color for profile {} set.**".format(section))

    @rankset.command(name = "color", pass_context=True, no_pm=True)
    async def rankcolors(self, ctx, section:str, color:str = None):
        """Set info color. e.g [p]lvlset rank color [exp|info] [default|white|hex|auto]"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        section = section.lower()
        default_info_color = (30, 30 ,30, 200)
        white_info_color = (255, 255, 255, 255)
        default_exp = (255, 255, 255, 230)
        default_a = 200

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("**Text-only commands allowed.**")
            return

        # get correct section for db query
        if section == "exp":
            section_name = "rank_exp_color"
        elif section == "info":
            section_name = "rank_info_color"
        elif section == "all":
            section_name = "all"
        else:
            await self.bot.say("**Not a valid section. (exp, info, all)**")
            return

        # get correct color choice
        if color == "auto":
            if section == "exp":
                color_ranks = [random.randint(2,3)]
            elif section == "info":
                color_ranks = [random.randint(0,1)]
            elif section == "all":
                color_ranks = [random.randint(2,3), random.randint(0,1)]

            hex_colors = await self._auto_color(userinfo["rank_background"], color_ranks)
            set_color = []
            for hex_color in hex_colors:
                color_temp = self._hex_to_rgb(hex_color, default_a)
                set_color.append(color_temp)
        elif color == "white":
            set_color = [white_info_color]
        elif color == "default":
            if section == "exp":
                set_color = [default_exp]
            elif section == "info":
                set_color = [default_info_color]
            elif section == "all":
                set_color = [default_exp, default_rep, default_badge, default_info_color]
        elif self._is_hex(color):
            set_color = [self._hex_to_rgb(color, default_a)]
        else:
            await self.bot.say("**Not a valid color. (default, hex, white, auto)**")
            return

        if section == "all":
            if len(set_color) == 1:
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "rank_exp_color": set_color[0],
                        "rank_info_color": set_color[0]
                    }})
            elif color == "default":
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "rank_exp_color": default_exp,
                        "rank_info_color": default_info_color
                    }})
            elif color == "auto":
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "rank_exp_color": set_color[0],
                        "rank_info_color": set_color[1]
                    }})
            await self.bot.say("**Colors for rank set.**")
        else:
            db.users.update_one({'user_id':user.id}, {'$set':{
                    section_name: set_color[0]
                }})
            await self.bot.say("**Color for rank {} set.**".format(section))

    @levelupset.command(name = "color", pass_context=True, no_pm=True)
    async def levelupcolors(self, ctx, section:str, color:str = None):
        """Set info color. e.g [p]lvlset color [info] [default|white|hex|auto]"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        section = section.lower()
        default_info_color = (30, 30 ,30, 200)
        white_info_color = (255, 255, 255, 255)
        default_a = 200

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("**Leveler commands for this server are disabled!**")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("**Text-only commands allowed.**")
            return

        # get correct section for db query
        if section == "info":
            section_name = "levelup_info_color"
        else:
            await self.bot.say("**Not a valid section. (info)**")
            return

        # get correct color choice
        if color == "auto":
            if section == "info":
                color_ranks = [random.randint(0,1)]
            hex_colors = await self._auto_color(userinfo["levelup_background"], color_ranks)
            set_color = []
            for hex_color in hex_colors:
                color_temp = self._hex_to_rgb(hex_color, default_a)
                set_color.append(color_temp)
        elif color == "white":
            set_color = [white_info_color]
        elif color == "default":
            if section == "info":
                set_color = [default_info_color]
        elif self._is_hex(color):
            set_color = [self._hex_to_rgb(color, default_a)]
        else:
            await self.bot.say("**Not a valid color. (default, hex, white, auto)**")
            return

        db.users.update_one({'user_id':user.id}, {'$set':{
                section_name: set_color[0]
            }})
        await self.bot.say("**Color for level-up {} set.**".format(section))

    # uses k-means algorithm to find color from bg, rank is abundance of color, descending
    async def _auto_color(self, url:str, ranks):
        phrases = ["Calculating colors..."] # in case I want more
        #try:
        await self.bot.say("**{}**".format(random.choice(phrases)))
        clusters = 10

        async with self.session.get(url) as r:
            image = await r.content.read()
        with open('data/leveler/temp_auto.png','wb') as f:
            f.write(image)

        im = Image.open('data/leveler/temp_auto.png').convert('RGBA')
        im = im.resize((290, 290)) # resized to reduce time
        ar = scipy.misc.fromimage(im)
        shape = ar.shape
        ar = ar.reshape(scipy.product(shape[:2]), shape[2])

        codes, dist = scipy.cluster.vq.kmeans(ar.astype(float), clusters)
        vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
        counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

        # sort counts
        freq_index = []
        index = 0
        for count in counts:
            freq_index.append((index, count))
            index += 1
        sorted_list = sorted(freq_index, key=operator.itemgetter(1), reverse=True)

        colors = []
        for rank in ranks:
            color_index = min(rank, len(codes))
            peak = codes[sorted_list[color_index][0]] # gets the original index
            peak = peak.astype(int)

            colors.append(''.join(format(c, '02x') for c in peak))
        return colors # returns array
        #except:
            #await self.bot.say("```Error or no scipy. Install scipy doing 'pip3 install numpy' and 'pip3 install scipy' or read here: https://github.com/AznStevy/Maybe-Useful-Cogs/blob/master/README.md```")

    # converts hex to rgb
    def _hex_to_rgb(self, hex_num: str, a:int):
        h = hex_num.lstrip('#')

        # if only 3 characters are given
        if len(str(h)) == 3:
            expand = ''.join([x*2 for x in str(h)])
            h = expand

        colors = [int(h[i:i+2], 16) for i in (0, 2 ,4)]
        colors.append(a)
        return tuple(colors)

    # dampens the color given a parameter
    def _moderate_color(self, rgb, a, moderate_num):
        new_colors = []
        for color in rgb[:3]:
            if color > 128:
                color -= moderate_num
            else:
                color += moderate_num
            new_colors.append(color)
        new_colors.append(230)

        return tuple(new_colors)


    @profileset.command(pass_context=True, no_pm=True)
    async def info(self, ctx, *, info):
        """Set your user info."""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        max_char = 150

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        if len(info) < max_char:
            db.users.update_one({'user_id':user.id}, {'$set':{"info": info}})
            await self.bot.say("**Your info section has been succesfully set!**")
        else:
            await self.bot.say("**Your description has too many characters! Must be <{}**".format(max_char))

    @levelupset.command(name = "bg", pass_context=True, no_pm=True)
    async def levelbg(self, ctx, *, image_name:str):
        """Set your level background"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("Text-only commands allowed!")
            return

        for bg in userinfo['lvlbackgrounds']:
            uinfo = userinfo['lvlbackgrounds'][bg]
            if uinfo['background_name'] == image_name:
                db.users.update_one({'user_id': userinfo['user_id']}, {'$set': {
                    "levelup_background": uinfo['bg_img'],
                }})
                await self.bot.say("Background **{}** successfully set!".format(uinfo['background_name']))
                break
        else:
            await self.bot.say("You don't own that background!")

    @profileset.command(name = "bg", pass_context=True, no_pm=True)
    async def profilebg(self, ctx, *, image_name:str):
        """Set your profile background"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("Text-only commands allowed!")
            return

        for bg in userinfo['backgrounds']:
            uinfo = userinfo['backgrounds'][bg]
            if uinfo['background_name'] == image_name:
                db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                    "profile_background":uinfo['bg_img'],
                    }})
                await self.bot.say("Background **{}** successfully set!".format(uinfo['background_name']))
                break
        else:
            await self.bot.say("You don't own that background!")

    @rankset.command(name = "bg", pass_context=True, no_pm=True)
    async def rankbg(self, ctx, *, image_name:str):
        """Set your rank background"""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        if "text_only" in self.settings and server.id in self.settings["text_only"]:
            await self.bot.say("Text-only commands allowed!")
            return

        for bg in userinfo['rankbackgrounds']:
            uinfo = userinfo['rankbackgrounds'][bg]
            if uinfo['background_name'] == image_name:
                db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                    "rank_background":uinfo['bg_img'],
                    }})
                await self.bot.say("Background **{}** successfully set!".format(uinfo['background_name']))
                break
        else:
            await self.bot.say("You don't own that background!")

    @profileset.command(pass_context=True, no_pm=True)
    async def title(self, ctx, *, title):
        """Set your title."""
        user = ctx.message.author
        server = ctx.message.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        max_char = 20

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        if len(title) < max_char:
            userinfo["title"] = title
            db.users.update_one({'user_id':user.id}, {'$set':{"title": title}})
            await self.bot.say("**Your title has been succesfully set!**")
        else:
            await self.bot.say("**Your title has too many characters! Must be <{}**".format(max_char))

    @checks.admin_or_permissions(manage_server=True)
    @commands.group(pass_context=True)
    async def lvladmin(self, ctx):
        """Admin Toggle Features"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.group(pass_context=True)
    async def overview(self, ctx):
        """A list of settings"""
        user = ctx.message.author

        disabled_servers = []
        private_levels = []
        disabled_levels = []
        locked_channels = []

        for server in self.bot.servers:
            if "disabled_servers" in self.settings.keys() and str(server.id) in self.settings["disabled_servers"]:
                disabled_servers.append(server.name)
            if "lvl_msg_lock" in self.settings.keys() and server.id in self.settings["lvl_msg_lock"].keys():
                for channel in server.channels:
                    if self.settings["lvl_msg_lock"][server.id] == channel.id:
                        locked_channels.append("\n{} → #{}".format(server.name,channel.name))
            if "lvl_msg" in self.settings.keys() and server.id in self.settings["lvl_msg"]:
                disabled_levels.append(server.name)
            if "private_lvl_msg" in self.settings.keys() and server.id in self.settings["private_lvl_msg"]:
                private_levels.append(server.name)

        num_users = 0
        for i in db.users.find({}):
            num_users += 1

        msg = ""
        msg += "**Servers:** {}\n".format(len(self.bot.servers))
        msg += "**Unique Users:** {}\n".format(num_users)
        if "mention" in self.settings.keys():
            msg += "**Mentions:** {}\n".format(str(self.settings["mention"]))
        msg += "**Background Price:** {}\n".format(self.settings["bg_price"])
        if "badge_type" in self.settings.keys():
            msg += "**Badge type:** {}\n".format(self.settings["badge_type"])
        msg += "**Disabled Servers:** {}\n".format(", ".join(disabled_servers))
        msg += "**Enabled Level Messages:** {}\n".format(", ".join(disabled_levels))
        msg += "**Private Level Messages:** {}\n".format(", ".join(private_levels))
        msg += "**Channel Locks:** {}\n".format(", ".join(locked_channels))
        em = discord.Embed(description=msg, colour=user.colour)
        em.set_author(name="Settings Overview for {}".format(self.bot.user.name))
        await self.bot.say(embed = em)
		
    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.command(name="chignore", pass_context=True, no_pm=True)
    async def __channelignore(self, ctx, channel:discord.Channel=None):
        """Set channels to ignore list."""
        server = ctx.message.server
        if channel == None:
            msg = ("{}lvladmin chignore <channel>\n\nSet channels to ignore list.".format(ctx.prefix))
            em = discord.Embed(description=msg, color=discord.Color.green())
            await self.bot.say(embed=em)
            return
        channeldb = db.channels.find_one({'server_id': server.id})
        if not channeldb:
            settings = {
                'server_id': server.id,
                'channels': {},
            }
            db.channels.insert_one(settings)

        channeldb = db.channels.find_one({'server_id': server.id})

        new_chan = {
            channel.id: channel.name
        }

        chan = channeldb['channels']
        chan_name = 'channels'

        try:
            if channel.id not in chan.keys():
                chan[channel.id] = new_chan
                db.channels.update_one({'server_id': server.id}, {'$set': {
                    chan_name: chan
                }})
                msg = ("Channel has been added to the ignore list!")
                em = discord.Embed(description=msg, color=discord.Color.green())
                await self.bot.say(embed=em)
                return

            elif channel.id in chan.keys():
                del chan[channel.id]
                db.channels.update_one({'server_id': server.id}, {'$set': {
                    chan_name: chan
                }})
                msg = ("Channel has been removed from the ignore list!")
                em = discord.Embed(description=msg, color=discord.Color.green())
                await self.bot.say(embed=em)
                return
        except:
            msg = ("Invalid Channel!")
            em = discord.Embed(description=msg, color=discord.Color.red())
            await self.bot.say(embed=em)

    @lvladmin.command(pass_context=True, no_pm=True)
    async def msgcredits(self, ctx, credits:int = 0):
        '''Credits per message logged. Default = 0'''
        channel = ctx.message.channel
        server = ctx.message.server

        if credits < 0 or credits > 1000:
            await self.bot.say("**Please enter a valid number (0 - 1000)**".format(channel.name))
            return

        if "msg_credits" not in self.settings.keys():
            self.settings["msg_credits"] = {}

        self.settings["msg_credits"][server.id] = credits
        await self.bot.say("**Credits per message logged set to `{}`.**".format(str(credits)))

        fileIO('data/leveler/settings.json', "save", self.settings)

    @lvladmin.command(name="lock", pass_context=True, no_pm=True)
    async def lvlmsglock(self, ctx):
        '''Locks levelup messages to one channel. Disable command via locked channel.'''
        channel = ctx.message.channel
        server = ctx.message.server

        if "lvl_msg_lock" not in self.settings.keys():
            self.settings["lvl_msg_lock"] = {}

        if server.id in self.settings["lvl_msg_lock"]:
            if channel.id == self.settings["lvl_msg_lock"][server.id]:
                del self.settings["lvl_msg_lock"][server.id]
                await self.bot.say("**Level-up message lock disabled.**".format(channel.name))
            else:
                self.settings["lvl_msg_lock"][server.id] = channel.id
                await self.bot.say("**Level-up message lock changed to `#{}`.**".format(channel.name))
        else:
            self.settings["lvl_msg_lock"][server.id] = channel.id
            await self.bot.say("**Level-up messages locked to `#{}`**".format(channel.name))

        fileIO('data/leveler/settings.json', "save", self.settings)

    async def _process_purchase(self, ctx):
        user = ctx.message.author
        server = ctx.message.server

        try:
            bank = self.bot.get_cog('Economy').bank
            if bank.account_exists(user) and self.settings["bg_price"] != 0:
                if not bank.can_spend(user, self.settings["bg_price"]):
                    await self.bot.say("**Insufficient funds. Backgrounds changes cost: ${}**".format(self.settings["bg_price"]))
                    return False
                else:
                    await self.bot.say('**{}, you are about to buy a background for `{}`. Confirm by typing `yes`.**'.format(self._is_mention(user), self.settings["bg_price"]))
                    answer = await self.bot.wait_for_message(timeout=15, author=user)
                    if answer is None:
                        await self.bot.say('**Purchase canceled.**')
                        return False
                    elif "yes" not in answer.content.lower():
                        await self.bot.say('**Background not purchased.**')
                        return False
                    else:
                        new_balance = bank.get_balance(user) - self.settings["bg_price"]
                        bank.set_credits(user, new_balance)
                        return True
            else:
                if self.settings["bg_price"] == 0:
                    return True
                else:
                    await self.bot.say("**You don't have an account. Do {}bank register**".format(prefix))
                    return False
        except:
            if self.settings["bg_price"] == 0:
                return True
            else:
                await self.bot.say("**There was an error with economy cog. Fix to allow purchases or set price to $0. Currently ${}**".format(prefix, self.settings["bg_price"]))
                return False
		
    async def _give_chat_credit(self, user, server):
        try:
            bank = self.bot.get_cog('Economy').bank
            if bank.account_exists(user) and "msg_credits" in self.settings:
                bank.deposit_credits(user, self.settings["msg_credits"][server.id])
        except:
            pass

    @checks.is_owner()
    @lvladmin.command(no_pm=True)
    async def setprice(self, price:int):
        '''Set a price for background changes.'''
        if price < 0:
            await self.bot.say("**That is not a valid background price.**")
        else:
            self.settings["bg_price"] = price
            await self.bot.say("**Background price set to: `{}`!**".format(price))
            fileIO('data/leveler/settings.json', "save", self.settings)

    @checks.is_owner()
    @lvladmin.command(pass_context=True, no_pm=True)
    async def setlevel(self, ctx, user : discord.Member, level:int):
        '''Set a user's level. (What a cheater C:).'''
        org_user = ctx.message.author
        server = user.server
        channel = ctx.message.channel
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        if level < 0:
            await self.bot.say("**Please enter a positive number.**")
            return

        # get rid of old level exp
        old_server_exp = 0
        for i in range(userinfo["servers"][server.id]["level"]):
            old_server_exp += self._required_exp(i)
        userinfo["total_exp"] -= old_server_exp
        userinfo["total_exp"] -= userinfo["servers"][server.id]["current_exp"]

        # add in new exp
        total_exp = self._level_exp(level)
        userinfo["servers"][server.id]["current_exp"] = 0
        userinfo["servers"][server.id]["level"] = level
        userinfo["total_exp"] += total_exp

        db.users.update_one({'user_id':user.id}, {'$set':{
            "servers.{}.level".format(server.id): level,
            "servers.{}.current_exp".format(server.id): 0,
            "total_exp": userinfo["total_exp"]
            }})
        await self.bot.say("**{}'s Level has been set to `{}`.**".format(self._is_mention(user), level))
        await self._handle_levelup(user, userinfo, server, channel)

    @checks.is_owner()
    @lvladmin.command(no_pm=True)
    async def mention(self):
        '''Toggle mentions on messages.'''
        if "mention" not in self.settings.keys() or self.settings["mention"] == True:
            self.settings["mention"] = False
            await self.bot.say("**Mentions disabled.**")
        else:
            self.settings["mention"] = True
            await self.bot.say("**Mentions enabled.**")
        fileIO('data/leveler/settings.json', "save", self.settings)

    async def _valid_image_url(self, url):
        max_byte = 1000

        try:
            async with self.session.get(url) as r:
                image = await r.content.read()
            with open('data/leveler/test.png','wb') as f:
                f.write(image)
            image = Image.open('data/leveler/test.png').convert('RGBA')
            os.remove('data/leveler/test.png')
            return True
        except:
            return False

    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.command(pass_context=True, no_pm=True)
    async def toggle(self, ctx):
        """Toggle most leveler commands on the current server."""
        server = ctx.message.server
        if server.id in self.settings["disabled_servers"]:
            self.settings["disabled_servers"] = list(filter(lambda a: a != server.id, self.settings["disabled_servers"]))
            await self.bot.say("**Leveler enabled on `{}`.**".format(server.name))
        else:
            self.settings["disabled_servers"].append(server.id)
            await self.bot.say("**Leveler disabled on `{}`.**".format(server.name))
        fileIO('data/leveler/settings.json', "save", self.settings)

    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.command(pass_context=True, no_pm=True)
    async def textonly(self, ctx, all:str=None):
        """Toggle text-based messages on the server."""
        server = ctx.message.server
        user = ctx.message.author
        # deals with enabled array

        if "text_only" not in self.settings.keys():
            self.settings["text_only"] = []

        if all != None:
            if user.id == self.owner:
                if all == "disableall":
                    self.settings["text_only"] = []
                    await self.bot.say("**Text-only disabled for all servers.**")
                elif all == "enableall":
                    self.settings["lvl_msg"] = []
                    for server in self.bot.servers:
                        self.settings["text_only"].append(server.id)
                    await self.bot.say("**Text-only messages enabled for all servers.**")
            else:
                await self.bot.say("**No Permission.**")
        else:
            if server.id in self.settings["text_only"]:
                self.settings["text_only"].remove(server.id)
                await self.bot.say("**Text-only messages disabled for `{}`.**".format(server.name))
            else:
                self.settings["text_only"].append(server.id)
                await self.bot.say("**Text-only messages enabled for `{}`.**".format(server.name))
        fileIO('data/leveler/settings.json', "save", self.settings)

    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.command(name="alerts", pass_context=True, no_pm=True)
    async def lvlalert(self, ctx, all:str=None):
        """Toggle level-up messages on the server."""
        server = ctx.message.server
        user = ctx.message.author

        # old version was boolean
        if not isinstance(self.settings["lvl_msg"], list):
            self.settings["lvl_msg"] = []

        if all != None:
            if user.id == self.owner:
                if all == "disableall":
                    self.settings["lvl_msg"] = []
                    await self.bot.say("**Level-up messages disabled for all servers.**")
                elif all == "enableall":
                    self.settings["lvl_msg"] = []
                    for server in self.bot.servers:
                        self.settings["lvl_msg"].append(server.id)
                    await self.bot.say("**Level-up messages enabled for all servers.**")
            else:
                await self.bot.say("**No Permission.**")
        else:
            if server.id in self.settings["lvl_msg"]:
                self.settings["lvl_msg"].remove(server.id)
                await self.bot.say("**Level-up alerts disabled for `{}`.**".format(server.name))
            else:
                self.settings["lvl_msg"].append(server.id)
                await self.bot.say("**Level-up alerts enabled for `{}`.**".format(server.name))
        fileIO('data/leveler/settings.json', "save", self.settings)

    @checks.admin_or_permissions(manage_server=True)
    @lvladmin.command(name="private", pass_context=True, no_pm=True)
    async def lvlprivate(self, ctx, all:str=None):
        """Toggles if lvl alert is a private message to the user."""
        server = ctx.message.server
        # deals with ENABLED array, not disabled

        if "private_lvl_msg" not in self.settings.keys():
            self.settings["private_lvl_msg"] = []

        if all != None:
            if user.id == self.owner:
                if all == "disableall":
                    self.settings["private_lvl_msg"] = []
                    await self.bot.say("**Private level-up messages disabled for all servers.**")
                elif all == "enableall":
                    self.settings["private_lvl_msg"] = []
                    for server in self.bot.servers:
                        self.settings["private_lvl_msg"].append(server.id)
                    await self.bot.say("**Private level-up messages enabled for all servers.**")
            else:
                await self.bot.say("**No Permission.**")
        else:
            if server.id in self.settings["private_lvl_msg"]:
                self.settings["private_lvl_msg"].remove(server.id)
                await self.bot.say("**Private level-up alerts disabled for `{}`.**".format(server.name))
            else:
                self.settings["private_lvl_msg"].append(server.id)
                await self.bot.say("**Private level-up alerts enabled for `{}`.**".format(server.name))

        fileIO('data/leveler/settings.json', "save", self.settings)

    @commands.group(pass_context=True)
    async def badge(self, ctx):
        """Badge Configuration Options"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @badge.command(name="available", pass_context=True, no_pm=True)
    async def available(self, ctx, global_badge:str = None):
        '''Get a list of available badges for server or 'global'.'''
        user = ctx.message.author
        server = ctx.message.server

        # get server stuff
        ids = [('global','Global',self.bot.user.avatar_url), (server.id, server.name, server.icon_url)]

        title_text = "**Available Badges**"
        index = 0
        for serverid, servername, icon_url in ids:
            em = discord.Embed(description='', colour=user.colour)
            em.set_author(name="{}".format(servername), icon_url = icon_url)
            msg = ""
            server_badge_info = db.badges.find_one({'server_id':serverid})
            if server_badge_info:
                server_badges = server_badge_info['badges']
                for badgename in server_badges:
                    badgeinfo = server_badges[badgename]
                    if badgeinfo['price'] == -1:
                        price = 'Non-purchasable'
                    elif badgeinfo['price'] == 0:
                        price = 'Free'
                    else:
                        price = badgeinfo['price']

                    msg += "**• {}** ({}) - {}\n".format(badgename, price, badgeinfo['description'])
            else:
                msg = "None"

            em.description = msg

            total_pages = 0
            for page in pagify(msg, ["\n"]):
                total_pages +=1

            counter = 1
            for page in pagify(msg, ["\n"]):
                if index == 0:
                    await self.bot.say(title_text, embed = em)
                else:
                    await self.bot.say(embed = em)
                index += 1

                em.set_footer(text = "Page {} of {}".format(counter, total_pages))
                counter += 1


    @badge.command(name="list", pass_context=True, no_pm=True)
    async def listuserbadges(self, ctx, user:discord.Member = None):
        '''Get the badges of a user.'''
        if user == None:
            user = ctx.message.author
        server = ctx.message.server
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)

        # sort
        priority_badges = []
        for badgename in userinfo['badges'].keys():
            badge = userinfo['badges'][badgename]
            priority_num = badge["priority_num"]
            if priority_num != -1:
                priority_badges.append((badge, priority_num))
        sorted_badges = sorted(priority_badges, key=operator.itemgetter(1), reverse=False)

        badge_ranks = ""
        counter = 1
        for badge, priority_num in sorted_badges[:12]:
            badge_ranks += "**{}. {}** ({}) [{}] **—** {}\n".format(counter, badge['badge_name'], badge['server_name'], priority_num, badge['description'])
            counter += 1
        if not badge_ranks:
            badge_ranks = "None"

        em = discord.Embed(description='', colour=user.colour)

        total_pages = 0
        for page in pagify(badge_ranks, ["\n"]):
            total_pages +=1

        counter = 1
        for page in pagify(badge_ranks, ["\n"]):
            em.description = page
            em.set_author(name="Badges for {}".format(user.name), icon_url = user.avatar_url)
            em.set_footer(text = "Page {} of {}".format(counter, total_pages))
            await self.bot.say(embed = em)
            counter += 1

    @badge.command(name="buy", pass_context=True, no_pm=True)
    async def buy(self, ctx, name:str, global_badge:str = None):
        '''Get a badge from repository. optional = "-global"'''
        user = ctx.message.author
        server = ctx.message.server
        if global_badge == '-global':
            serverid = 'global'
        else:
            serverid = server.id
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)
        server_badge_info = db.badges.find_one({'server_id':serverid})

        if server_badge_info:
            server_badges = server_badge_info['badges']
            if name in server_badges:

                if "{}_{}".format(name,str(serverid)) not in userinfo['badges'].keys():
                    badge_info = server_badges[name]
                    if badge_info['price'] == -1:
                        await self.bot.say('**That badge is not purchasable.**'.format(name))
                    elif badge_info['price'] == 0:
                        userinfo['badges']["{}_{}".format(name,str(serverid))] = server_badges[name]
                        db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                            "badges":userinfo['badges'],
                            }})
                        await self.bot.say('**`{}` has been obtained.**'.format(name))
                    else:
                        # use the economy cog
                        bank = self.bot.get_cog('Economy').bank
                        await self.bot.say('**{}, you are about to buy the `{}` badge for `{}`. Confirm by typing "yes"**'.format(self._is_mention(user), name, badge_info['price']))
                        answer = await self.bot.wait_for_message(timeout=15, author=user)
                        if answer is None:
                            await self.bot.say('**Purchase canceled.**')
                            return
                        elif "yes" not in answer.content.lower():
                            await self.bot.say('**Badge not purchased.**')
                            return
                        else:
                            if bank.account_exists(user) and badge_info['price'] <= bank.get_balance(user):
                                bank.withdraw_credits(user, badge_info['price'])
                                userinfo['badges']["{}_{}".format(name,str(serverid))] = server_badges[name]
                                db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                                    "badges":userinfo['badges'],
                                    }})
                                await self.bot.say('**You have bought the `{}` badge for `{}`.**'.format(name, badge_info['price']))
                            elif bank.account_exists(user) and bank.get_balance(user) < badge_info['price']:
                                await self.bot.say('**Not enough money! Need `{}` more.**'.format(badge_info['price'] - bank.get_balance(user)))
                            else:
                                await self.bot.say('**User does not exist in bank. Do {}bank register**'.format(prefix))
                else:
                    await self.bot.say('**{}, you already have this badge!**'.format(user.name))
            else:
                await self.bot.say('**The badge `{}` does not exist. (try `{}badge available`)**'.format(name, ctx.prefix))
        else:
            await self.bot.say('**There are no badges to get! (try `{}badge get [name] -global`).**'.format(ctx.prefix))

    @badge.command(name="set", pass_context=True, no_pm=True)
    async def set(self, ctx, name:str, priority_num:int):
        '''Set a badge to profile. -1(invis), 0(not on profile), max: 5000.'''
        user = ctx.message.author
        server = ctx.message.author
        await self._create_user(user, server)

        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)

        if priority_num < -1 or priority_num > 5000:
            await self.bot.say("**Invalid priority number! -1-5000**")
            return

        for badge in userinfo['badges']:
            if userinfo['badges'][badge]['badge_name'] == name:
                userinfo['badges'][badge]['priority_num'] = priority_num
                db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                    "badges":userinfo['badges'],
                    }})
                await self.bot.say("**The `{}` badge priority has been set to `{}`!**".format(userinfo['badges'][badge]['badge_name'], priority_num))
                break
        else:
            await self.bot.say("**You don't have that badge!**")

    def _badge_convert_dict(self, userinfo):
        if 'badges' not in userinfo or not isinstance(userinfo['badges'], dict):
            db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                "badges":{},
                }})
        return db.users.find_one({'user_id':userinfo['user_id']})

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(name="add", pass_context = True, no_pm=True)
    async def addbadge(self, ctx, name:str, bg_img:str, price:int, *, description:str):
        """Add a badge. name = "Use Quotes", Colors = #hex. bg_img = url, price = -1(non-purchasable), 0,..."""

        user = ctx.message.author
        server = ctx.message.server

        # check members
        required_members = 35
        members = 0
        for member in server.members:
            if not member.bot:
                members += 1

        if user.id == self.owner:
            pass
        elif members < required_members:
            await self.bot.say("**You may only add badges in servers with {}+ non-bot members**".format(required_members))
            return

        if '-global' in description and user.id == self.owner:
            description = description.replace('-global', '')
            serverid = 'global'
            servername = 'global'
        else:
            serverid = server.id
            servername = server.name

        if '.' in name:
            await self.bot.say("**Name cannot contain `.`**")
            return

        if not await self._valid_image_url(bg_img):
            await self.bot.say("**Background is not valid. Enter hex or image url!**")
            return

        if price < -1:
            await self.bot.say("**Price is not valid!**")
            return

        if len(description.split(" ")) > 40:
            await self.bot.say("**Description is too long! <=40**")
            return

        badges = db.badges.find_one({'server_id':serverid})
        if not badges:
            db.badges.insert_one({'server_id':serverid,
                'badges': {}})
            badges = db.badges.find_one({'server_id':serverid})

        new_badge = {
                "badge_name": name,
                "bg_img": bg_img,
                "price": price,
                "description": description,
                #"border_color": border_color,
                "server_id": serverid,
                "server_name": servername,
                "priority_num": 0
            }

        if name not in badges['badges'].keys():
            # create the badge regardless
            badges['badges'][name] = new_badge
            db.badges.update_one({'server_id':serverid}, {'$set': {
                'badges': badges['badges']
                }})
            await self.bot.say("**`{}` Badge added in `{}` server.**".format(name, servername))
        else:
            # update badge in the server
            badges['badges'][name] = new_badge
            db.badges.update_one({'server_id':serverid}, {'$set': {
                'badges': badges['badges']
                }})

            # go though all users and update the badge. Doing it this way because dynamic does more accesses when doing profile
            for user in db.users.find({}):
                try:
                    user = self._badge_convert_dict(user)
                    userbadges = user['badges']
                    badge_name = "{}_{}".format(name, serverid)
                    if badge_name in userbadges.keys():
                        user_priority_num = userbadges[badge_name]['priority_num']
                        new_badge['priority_num'] = user_priority_num # maintain old priority number set by user
                        userbadges[badge_name] = new_badge
                        db.users.update_one({'user_id':user['user_id']}, {'$set': {
                            'badges': userbadges
                            }})
                except:
                    pass
            await self.bot.say("**The `{}` badge has been updated**".format(name))

    @checks.is_owner()
    @badge.command(no_pm=True)
    async def type(self, name:str):
        """circles or bars."""
        valid_types = ["circles", "bars"]
        if name.lower() not in valid_types:
            await self.bot.say("**That is not a valid badge type!**")
            return

        self.settings["badge_type"] = name.lower()
        await self.bot.say("**Badge type set to `{}`**".format(name.lower()))
        fileIO('data/leveler/settings.json', "save", self.settings)

    def _is_hex(self, color:str):
        if color != None and len(color) != 4 and len(color) != 7:
            return False

        reg_ex = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
        return re.search(reg_ex, str(color))

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(name="delete", pass_context=True, no_pm=True)
    async def delbadge(self, ctx, *, name:str):
        """Delete a badge and remove from all users."""
        user = ctx.message.author
        channel = ctx.message.channel
        server = user.server

        #return

        if '-global' in name and user.id == self.owner:
            name = name.replace(' -global', '')
            serverid = 'global'
        else:
            serverid = server.id

        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        serverbadges = db.badges.find_one({'server_id':serverid})
        if name in serverbadges['badges'].keys():
            del serverbadges['badges'][name]
            db.badges.update_one({'server_id':serverbadges['server_id']}, {'$set':{
                "badges":serverbadges["badges"],
                }})
            # remove the badge if there
            for user_info_temp in db.users.find({}):
                try:
                    user_info_temp = self._badge_convert_dict(user_info_temp)

                    badge_name = "{}_{}".format(name, serverid)
                    if badge_name in user_info_temp["badges"].keys():
                        del user_info_temp["badges"][badge_name]
                        db.users.update_one({'user_id':user_info_temp['user_id']}, {'$set':{
                            "badges":user_info_temp["badges"],
                            }})
                except:
                    pass

            await self.bot.say("**The `{}` badge has been removed.**".format(name))
        else:
            await self.bot.say("**That badge does not exist.**")

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(pass_context = True, no_pm=True)
    async def give(self, ctx, user : discord.Member, name: str):
        """Give a user a badge with a certain name"""
        org_user = ctx.message.author
        server = org_user.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        if '-global' in name and org_user.id == self.owner:
            name = name.replace(' -global', '')
            serverid = 'global'
        else:
            serverid = server.id

        try:
            serverbadges = db.badges.find_one({'server_id':serverid})
            badges = serverbadges['badges']
            badge_name = "{}_{}".format(name, serverid)
        except:
            await self.bot.say("**You don't have permission for that badge!**")
            return

        if name not in badges:
            await self.bot.say("**That badge doesn't exist in this server!**")
            return
        elif badge_name in badges.keys():
            await self.bot.say("**{} already has that badge!**".format(self._is_mention(user)))
            return
        else:
            userinfo["badges"][badge_name] = badges[name]
            db.users.update_one({'user_id':user.id}, {'$set':{"badges": userinfo["badges"]}})
            await self.bot.say("{} has just given {} the **{}** badge!".format(self._is_mention(org_user), self._is_mention(user), name))

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(pass_context = True, no_pm=True)
    async def take(self, ctx, user : discord.Member, name: str):
        """Take a user's badge."""
        org_user = ctx.message.author
        server = org_user.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._badge_convert_dict(userinfo)

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled.")
            return

        if '-global' in name and org_user.id == self.owner:
            name = name.replace(' -global', '')
            serverid = 'global'
        else:
            serverid = server.id

        try:
            serverbadges = db.badges.find_one({'server_id':serverid})
            badges = serverbadges['badges']
            badge_name = "{}_{}".format(name, serverid)
        except:
            await self.bot.say("**You don't have permission for that badge!**")
            return

        if name not in badges:
            await self.bot.say("**That badge doesn't exist in this server!**")
        elif badge_name not in userinfo["badges"]:
            await self.bot.say("**{} does not have that badge!**".format(self._is_mention(user)))
        else:
            if userinfo['badges'][badge_name]['price'] == -1:
                del userinfo["badges"][badge_name]
                db.users.update_one({'user_id':user.id}, {'$set':{"badges": userinfo["badges"]}})
                await self.bot.say("{} has taken the **{}** badge from {}! :upside_down:".format(self._is_mention(org_user), name, self._is_mention(user)))
            else:
                await self.bot.say("**You can't take away purchasable badges!**")

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(name = 'link', no_pm=True, pass_context=True)
    async def linkbadge(self, ctx, badge_name:str, level:int):
        """Associate a badge with a level."""
        server = ctx.message.server
        serverbadges = db.badges.find_one({'server_id':server.id})

        if serverbadges == None:
            await self.bot.say("**This server does not have any badges!**")
            return

        if badge_name not in serverbadges['badges'].keys():
            await self.bot.say("**Please make sure the `{}` badge exists!**".format(badge_name))
            return
        else:
            server_linked_badges = db.badgelinks.find_one({'server_id':server.id})
            if not server_linked_badges:
                new_server = {
                    'server_id': server.id,
                    'badges': {
                        badge_name:str(level)
                    }
                }
                db.badgelinks.insert_one(new_server)
            else:
                server_linked_badges['badges'][badge_name] = str(level)
                db.badgelinks.update_one({'server_id':server.id}, {'$set':{'badges':server_linked_badges['badges']}})
            await self.bot.say("**The `{}` badge has been linked to level `{}`**".format(badge_name, level))

    @checks.admin_or_permissions(manage_roles=True)
    @badge.command(name = 'unlink', no_pm=True, pass_context=True)
    async def unlinkbadge(self, ctx, badge_name:str):
        """Delete a badge/level association."""
        server = ctx.message.server

        server_linked_badges = db.badgelinks.find_one({'server_id':server.id})
        badge_links = server_linked_badges['badges']

        if badge_name in badge_links.keys():
            await self.bot.say("**Badge/Level association `{}`/`{}` removed.**".format(badge_name, badge_links[badge_name]))
            del badge_links[badge_name]
            db.badgelinks.update_one({'server_id':server.id},{'$set':{'badges':badge_links}})
        else:
            await self.bot.say("**The `{}` badge is not linked to any levels!**".format(badge_name))

    @checks.mod_or_permissions(manage_roles=True)
    @badge.command(name = 'listlinks', no_pm=True, pass_context=True)
    async def listbadge(self, ctx):
        """List level/badge associations."""
        server = ctx.message.server
        user = ctx.message.author

        server_badges = db.badgelinks.find_one({'server_id':server.id})

        em = discord.Embed(description='', colour=user.colour)
        em.set_author(name="Current Badge - Level Links for {}".format(server.name), icon_url = server.icon_url)

        if server_badges == None or 'badges' not in server_badges or server_badges['badges'] == {}:
            msg = 'None'
        else:
            badges = server_badges['badges']
            msg = '**Badge** → Level\n'
            for badge in badges.keys():
                msg += '**• {} →** {}\n'.format(badge, badges[badge])

        em.description = msg
        await self.bot.say(embed = em)

    @commands.group(pass_context=True)
    async def role(self, ctx):
        """Admin Background Configuration"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @checks.mod_or_permissions(manage_roles=True)
    @role.command(name = 'link', no_pm=True, pass_context=True)
    async def linkrole(self, ctx, role_name:str, level:int, remove_role = None):
        """Associate a role with a level. Removes previous role if given."""
        server = ctx.message.server

        role_obj = discord.utils.find(lambda r: r.name == role_name, server.roles)
        remove_role_obj = discord.utils.find(lambda r: r.name == remove_role, server.roles)
        if role_obj == None or (remove_role != None and remove_role_obj == None):
            if remove_role == None:
                await self.bot.say("**Please make sure the `{}` role exists!**".format(role_name))
            else:
                await self.bot.say("**Please make sure the `{}` and/or `{}` roles exist!**".format(role_name, remove_role))
        else:
            server_roles = db.roles.find_one({'server_id':server.id})
            if not server_roles:
                new_server = {
                    'server_id': server.id,
                    'roles': {
                        role_name: {
                            'level':str(level),
                            'remove_role': remove_role
                            }
                    }
                }
                db.roles.insert_one(new_server)
            else:
                if role_name not in server_roles['roles']:
                    server_roles['roles'][role_name] = {}

                server_roles['roles'][role_name]['level'] = str(level)
                server_roles['roles'][role_name]['remove_role'] = remove_role
                db.roles.update_one({'server_id':server.id}, {'$set':{'roles':server_roles['roles']}})

            if remove_role == None:
                await self.bot.say("**The `{}` role has been linked to level `{}`**".format(role_name, level))
            else:
                await self.bot.say("**The `{}` role has been linked to level `{}`. Will also remove `{}` role.**".format(
                    role_name, level, remove_role))

    @checks.mod_or_permissions(manage_roles=True)
    @role.command(name = 'unlink', no_pm=True, pass_context=True)
    async def unlinkrole(self, ctx, role_name:str):
        """Delete a role/level association."""
        server = ctx.message.server

        server_roles = db.roles.find_one({'server_id':server.id})
        roles = server_roles['roles']

        if role_name in roles:
            await self.bot.say("**Role/Level association `{}`/`{}` removed.**".format(role_name, roles[role_name]['level']))
            del roles[role_name]
            db.roles.update_one({'server_id':server.id},{'$set':{'roles':roles}})
        else:
            await self.bot.say("**The `{}` role is not linked to any levels!**".format(role_name))

    @checks.mod_or_permissions(manage_roles=True)
    @role.command(name = 'listlinks', no_pm=True, pass_context=True)
    async def listrole(self, ctx):
        """List level/role associations."""
        server = ctx.message.server
        user = ctx.message.author

        server_roles = db.roles.find_one({'server_id':server.id})

        em = discord.Embed(description='', colour=user.colour)
        em.set_author(name="Current Role - Level Links for {}".format(server.name), icon_url = server.icon_url)

        if server_roles == None or 'roles' not in server_roles or server_roles['roles'] == {}:
            msg = 'None'
        else:
            roles = server_roles['roles']
            msg = '**Role** → Level\n'
            for role in roles:
                if roles[role]['remove_role'] != None:
                    msg += '**• {} →** {} (Removes: {})\n'.format(role, roles[role]['level'], roles[role]['remove_role'])
                else:
                    msg += '**• {} →** {}\n'.format(role, roles[role]['level'])

        em.description = msg
        await self.bot.say(embed = em)

    @lvladmin.group(name = "bg", pass_context=True)
    async def lvladminbg(self, ctx):
        """Admin Background Configuration"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @checks.is_owner()
    @lvladminbg.command(name="custom", no_pm=True, pass_context=True)
    async def setcustombg(self, ctx, bg_type:str, user_id:str, img_url:str):
        """Set one-time custom background"""
        valid_types = ['profile', 'rank', 'levelup']
        type_input = bg_type.lower()

        if type_input not in valid_types:
            await self.bot.say('Please choose a valid type: `profile`, `rank`, `levelup`.')
            return

        userinfo = db.users.find_one({'user_id': user_id})
        if type_input == "profile":
            userinfox = 'backgrounds'
        elif type_input == "rank":
            userinfox = 'rankbackgrounds'
        elif type_input == "levelup":
            userinfox = 'lvlbackgrounds'

        # test if valid user_id
        if not userinfo:
            await self.bot.say("That is not a valid user id!")
            return

        if not await self._valid_image_url(img_url):
            await self.bot.say("That is not a valid image url!")
            return

        def_bg = {
                "background_name": "custom",
                "bg_img": img_url,
                "price": 0,
            }
        db.users.update_one({'user_id': user_id}, {'$set': {
                    userinfox + ".custom": def_bg,
                }}, upsert=True)
        db.users.update_one({'user_id':user_id}, {'$set':{"{}_background".format(type_input): img_url}})
        await self.bot.say("User {} custom {} background set.".format(user_id, bg_type))


    @commands.group(pass_context=True, no_pm=True)
    async def lvlshop(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @lvlshop.command(name="buy", pass_context=True, no_pm=True)
    async def _lvlbuy(self, ctx, type:str, *, name:str):
        """Buy Backgrounds from the shop"""
        user = ctx.message.author
        server = ctx.message.server
        serverid = 'global'
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._bg_convert_dict(userinfo)
        server_bg_info = db.backgrounds.find_one({'server_id':serverid})

        if server_bg_info:
            if type.lower() == "profile":
                server_bgs = server_bg_info['backgrounds']
                userinfox = userinfo['backgrounds']
                bgx = "backgrounds"
                xname = "Profile"
            elif type.lower() == "rank":
                server_bgs = server_bg_info['rankbackgrounds']
                userinfox = userinfo['rankbackgrounds']
                bgx = "rankbackgrounds"
                xname = "Rank"
            elif type.lower() == "levelup":
                server_bgs = server_bg_info['lvlbackgrounds']
                userinfox = userinfo['lvlbackgrounds']
                bgx = "lvlbackgrounds"
                xname = "Levelup"
            else:
                await self.bot.say("{}lvlshop buy <type> <bg_name>\n"
                                   "type = profile, rank, levelup".format(ctx.prefix))
                return

            if name in server_bgs:
                if "{}".format(name) not in userinfox.keys():
                    bg_info = server_bgs[name]
                    if bg_info['price'] == -1:
                        await self.bot.say('That {} background is not purchasable!'.format(xname))
                    elif bg_info['price'] == 0:
                        userinfox["{}".format(name)] = server_bgs[name]
                        db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                            bgx:userinfox,
                            }})
                        await self.bot.say('**{}** has been purchased!'.format(name))
                    else:
                        # use the economy cog
                        bank = self.bot.get_cog('Economy').bank
                        await self.bot.say('**{}**, you are about to buy the {} background **{}** for **{} credits**. Confirm by typing *"yes"*'.format(self._is_mention(user), xname, name, bg_info['price']))
                        answer = await self.bot.wait_for_message(timeout=15, author=user)
                        if answer is None:
                            await self.bot.say('Purchase canceled!')
                            return
                        elif "yes" not in answer.content.lower():
                            await self.bot.say('Background not purchased!')
                            return
                        else:
                            if bank.account_exists(user) and bg_info['price'] <= bank.get_balance(user):
                                bank.withdraw_credits(user, bg_info['price'])
                                userinfox["{}".format(name)] = server_bgs[name]
                                db.users.update_one({'user_id':userinfo['user_id']}, {'$set':{
                                    bgx:userinfox,
                                    }})
                                await self.bot.say('You have bought the background **{}** for **{} credits**!'.format(name, bg_info['price']))
                            elif bank.account_exists(user) and bank.get_balance(user) < bg_info['price']:
                                await self.bot.say('Not enough credits! Need **{} credits** more!'.format(bg_info['price'] - bank.get_balance(user)))
                            else:
                                await self.bot.say('You don\'t have a bank account. Please use **{}bank register**'.format(prefix))
                else:
                    await self.bot.say('**{}**, you already have this background!'.format(user.name))
            else:
                await self.bot.say('The background **{}** does not exist. (try **{}lvlshop list**)'.format(name, ctx.prefix))


    @lvlshop.command(name="add", pass_context=True, no_pm=True)
    @checks.is_owner()
    async def _lvlshadd(self, ctx, type:str, bg_img:str, price:int, *, name:str):
        """Add Backgrounds to the shop"""
        user = ctx.message.author
        server = ctx.message.server

        serverid = 'global'

        if '.' in name:
            await self.bot.say("Name can't contain `.`")
            return

        if not await self._valid_image_url(bg_img):
            await self.bot.say("Invalid Background. Enter hex or image url!")
            return

        if price < -1:
            await self.bot.say("Price is not valid!")
            return

        bgs = db.backgrounds.find_one({'server_id':serverid})
		
        if not bgs:
            settings = {
                'backgrounds': {},
                'rankbackgrounds': {},
                'lvlbackgrounds': {},
                'server_id': serverid
            }
            db.backgrounds.insert_one(settings)
        bgs = db.backgrounds.find_one({'server_id':serverid})

        new_bg = {
                "background_name": name,
                "bg_img": bg_img,
                "price": price,
            }

        if type.lower() == "profile":
            xbgs = bgs['backgrounds']
            xbg = "backgrounds"
            def_imgx = "http://i.imgur.com/8T1FUP5.jpg"
            xname = "Profile"
        elif type.lower() == "rank":
            xbgs = bgs['rankbackgrounds']
            xbg = "rankbackgrounds"
            def_imgx = "http://i.imgur.com/SorwIrc.jpg"
            xname = "Rank"
        elif type.lower() == "levelup":
            xbgs = bgs['lvlbackgrounds']
            xbg = "lvlbackgrounds"
            def_imgx = "http://i.imgur.com/eEFfKqa.jpg"
            xname = "Levelup"
        else:
            await self.bot.say("{}lvlshop add <type> <link> <price> <bg_name>\n"
                               "type = profile, rank, levelup".format(ctx.prefix))
            return

        if name not in xbgs.keys():
            # create the background regardless
            xbgs[name] = new_bg
            db.backgrounds.update_one({'server_id':serverid}, {'$set': {
                xbg: xbgs
                }})
            await self.bot.say("{} background **{}** has been added!".format(xname, name))
        else:
            # update background in the server
            xbgs[name] = new_bg
            db.backgrounds.update_one({'server_id':serverid}, {'$set': {
                xbg: xbgs
                }})

            # go through all users and update the background. Doing it this way because dynamic does more accesses when doing profile
            for user in db.users.find({}):
                try:
                    if type.lower() == "profile":
                        xuser = user['backgrounds']
                    elif type.lower() == "rank":
                        xuser = user['rankbackgrounds']
                    elif type.lower() == "levelup":
                        xuser = user['lvlbackgrounds']
                    user = self._bg_convert_dict(user)
                    userbgs = xuser
                    bg_name = "{}".format(name)
                    if bg_name in userbgs.keys():
                        userbgs[bg_name] = new_bg
                        db.users.update_one({'user_id':user['user_id']}, {'$set': {
                            xbg: userbgs
                            }})
                except:
                    pass
            await self.bot.say("{} background **{}** has been updated!".format(xname, name))

        if "default" not in xbgs.keys():
            def_bg = {
                "background_name": "default",
                "bg_img": def_imgx,
                "price": 0,
            }
            xbgs["default"] = def_bg
            db.backgrounds.update_one({'server_id': serverid}, {'$set': {
                xbg: xbgs
            }})
            for user in db.users.find({}):
                try:
                    if type == "profile":
                        xuser = user['backgrounds']
                    elif type == "rank":
                        xuser = user['rankbackgrounds']
                    elif type == "levelup":
                        xuser = user['lvlbackgrounds']
                    user = self._bg_convert_dict(user)
                    userbgs = xuser
                    bg_name = "default"
                    if bg_name in userbgs.keys():
                        userbgs[bg_name] = def_bg
                        db.users.update_one({'user_id':user['user_id']}, {'$set': {
                            xbg: userbgs
                            }})
                except:
                    pass
					
    @lvlshop.command(name="fix", pass_context=True, no_pm=True)
    @checks.is_owner()
    async def _lvlshfix(self, ctx, type:str):
        """Fixes the default background for all users"""
        user = ctx.message.author
        server = ctx.message.server

        serverid = 'global'

        userxz = self._create_user(server, user)

        bgs = db.backgrounds.find_one({'server_id':serverid})

        if type.lower() == "profile":
            xbgs = bgs['backgrounds']
            xbg = "backgrounds"
            def_imgx = "http://i.imgur.com/8T1FUP5.jpg"
            xname = "Profile"
        elif type.lower() == "rank":
            xbgs = bgs['rankbackgrounds']
            xbg = "rankbackgrounds"
            def_imgx = "http://i.imgur.com/SorwIrc.jpg"
            xname = "Rank"
        elif type.lower() == "levelup":
            xbgs = bgs['lvlbackgrounds']
            xbg = "lvlbackgrounds"
            def_imgx = "http://i.imgur.com/eEFfKqa.jpg"
            xname = "Levelup"
        else:
            await self.bot.say('{}lvlshop fix <type>\ntype = profile, rank, levelup'.format(ctx.prefix))
            return

        name = "default"

        if "xdefault" not in xbgs.keys():
            def_bg = {
                "background_name": "default",
                "bg_img": def_imgx,
                "price": 0,
            }
            xbgs["default"] = def_bg
            db.backgrounds.update_one({'server_id': serverid}, {'$set': {
                xbg: xbgs
            }})
            for user in db.users.find({}):
                try:
                    if type == "profile":
                        xuser = user['backgrounds']
                    elif type == "rank":
                        xuser = user['rankbackgrounds']
                    elif type == "levelup":
                        xuser = user['lvlbackgrounds']
                    user = self._bg_convert_dict(user)
                    userbgs = xuser
                    bg_name = "default"
                    if bg_name in userbgs.keys():
                        userbgs[bg_name] = def_bg
                        db.users.update_one({'user_id':user['user_id']}, {'$set': {
                            xbg: userbgs
                            }})
                except:
                    pass
            await self.bot.say("{} background **{}** has been updated!".format(xname, name))

    @lvlshop.command(name="del", pass_context=True, no_pm=True)
    @checks.is_owner()
    async def _lvlshdel(self, ctx, type:str, *, name:str):
        """Remove backgrounds from the shop"""
        user = ctx.message.author
        channel = ctx.message.channel
        server = user.server

        #return
        serverid = 'global'

        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._bg_convert_dict(userinfo)

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        if not type:
            await self.bot.say("{}lvlshop del <type> <link> <price> <bg_name>\n"
                               "type = profile, rank, levelup".format(ctx.prefix))
            return

        bgs = db.backgrounds.find_one({'server_id':serverid})

        if type.lower() == "profile":
            xbgs = bgs['backgrounds']
            xbg = "backgrounds"
            xname = "Profile"
        elif type.lower() == "rank":
            xbgs = bgs['rankbackgrounds']
            xbg = "rankbackgrounds"
            xname = "Rank"
        elif type.lower() == "levelup":
            xbgs = bgs['lvlbackgrounds']
            xbg = "lvlbackgrounds"
            xname = "Levelup"
        else:
            await self.bot.say(("{}lvlshop del <type> <link> <price> <bg_name>\n"
                                "type = profile, rank, levelup".format(ctx.prefix)))
            return

        if name in xbgs.keys():
            del xbgs[name]
            db.backgrounds.update_one({'server_id':bgs['server_id']}, {'$set':{
                xbg:xbgs,
                }})

            try:
                for user_info_temp in db.users.find({}):
                    if type.lower() == "profile":
                        xuser = user_info_temp['backgrounds']
                    elif type.lower() == "rank":
                        xuser = user_info_temp['rankbackgrounds']
                    elif type.lower() == "levelup":
                        xuser = user_info_temp['lvlbackgrounds']
                    try:
                        user_info_temp = self._bg_convert_dict(user_info_temp)

                        bg_name = "{}".format(name)
                        if bg_name in xuser.keys():
                            del xuser[bg_name]
                            db.users.update_one({'user_id':user_info_temp['user_id']}, {'$set':{
                                xbg:xuser,
                                }})
                    except:
                        pass
            except:
                pass

            await self.bot.say("{} background **{}** has been removed!".format(xname, name))
        else:
            await self.bot.say("That {} background does not exist!".format(xname))

    @lvlshop.command(name="give", pass_context=True, no_pm=True)
    @checks.is_owner()
    async def _lvlshgive(self, ctx, type:str, user : discord.Member, *, name: str):
        """Give background to users for free"""
        org_user = ctx.message.author
        server = org_user.server
        # creates user if doesn't exist
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id':user.id})
        userinfo = self._bg_convert_dict(userinfo)

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        serverid = 'global'

        bgs = db.backgrounds.find_one({'server_id':serverid})

        if type.lower() == "profile":
            xbgs = bgs['backgrounds']
            xbg = "backgrounds"
            xuser = userinfo['backgrounds']
            xname = "Profile"
        elif type.lower() == "rank":
            xbgs = bgs['rankbackgrounds']
            xbg = "rankbackgrounds"
            xuser = userinfo['rankbackgrounds']
            xname = "Rank"
        elif type.lower() == "levelup":
            xbgs = bgs['lvlbackgrounds']
            xbg = "lvlbackgrounds"
            xuser = userinfo['lvlbackgrounds']
            xname = "Levelup"


        bg_name = "{}".format(name)

        if name not in xbgs:
            message = ("That background doesn't exist!")
            await self.bot.say("That background doesn't exist!")
            return
        elif bg_name in xuser.keys():
            await self.bot.say("**{}** already owns that {} background!".format(self._is_mention(user), xname))
            return
        else:
            xuser[bg_name] = xbgs[name]
            db.users.update_one({'user_id':user.id}, {'$set':{xbg: xuser}})
            await self.bot.say("**{}** has just given **{}** the {} background **{}**!"
                               "".format(org_user.name, user.name, xname, name))


    @lvlshop.command(name="inv", pass_context=True, no_pm=True)
    async def _lvlinv(self, ctx, user: discord.Member = None):
        """Shows purchased backgrounds."""
        if user == None:
            user = ctx.message.author
        server = ctx.message.server
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id': user.id})

        # sort
        listbgs = []
        listrbgs = []
        listlbgs = []

        for bgname in userinfo['backgrounds'].keys():
            bg = userinfo['backgrounds'][bgname]
            listbgs.append((bg))

        for rbgname in userinfo['rankbackgrounds'].keys():
            rbg = userinfo['rankbackgrounds'][rbgname]
            listrbgs.append((rbg))

        for lbgname in userinfo['lvlbackgrounds'].keys():
            lbg = userinfo['lvlbackgrounds'][lbgname]
            listlbgs.append((lbg))

        bg_ranks = ""
        counter = 1
        for bg in listbgs:
            bg_ranks += "{}\n".format(bg['background_name'])
            counter += 1
        if not bg_ranks:
            bg_ranks = "None\n"

        rbg_ranks = ""
        rcounter = 1
        for rbg in listrbgs:
            rbg_ranks += "{}\n".format(rbg['background_name'])
            rcounter += 1
        if not rbg_ranks:
            rbg_ranks = "None\n"

        lbg_ranks = ""
        lcounter = 1
        for lbg in listlbgs:
            lbg_ranks += "{}\n".format(lbg['background_name'])
            lcounter += 1
        if not lbg_ranks:
            lbg_ranks = "None\n"

        em = discord.Embed(description='', colour=user.colour)

        bgx_ranks = bg_ranks + rbg_ranks + lbg_ranks

        total_pages = 0
        for page in pagify(bgx_ranks, ["\n"]):
            total_pages += 1

        counter = 1
        for page in pagify(bg_ranks, ["\n"]):
            em.description = u'\u2063\n' + "**Profile:**\n{}\n**Rank:**\n{}\n**Levelup:**\n{}".format(bg_ranks, rbg_ranks, lbg_ranks)#page
            em.set_author(name="Backgrounds for {}".format(user.name), icon_url=user.avatar_url)
            em.set_footer(text="Page {} of {}".format(counter, total_pages))
            await self.bot.say(embed=em)
            counter += 1

    @lvlshop.command(name = 'list', pass_context=True, no_pm=True)
    async def _lvlshbgs(self, ctx, type:str = None):
        """Lists backgrounds from the shop"""
        server = ctx.message.server
        user = ctx.message.author
        max_all = 18
        await self._create_user(user, server)
        userinfo = db.users.find_one({'user_id': user.id})
        serverid = "global"
        bginfo = db.backgrounds.find_one({'server_id': serverid})

        if not  bginfo:
            settings = {
                'backgrounds': {},
                'rankbackgrounds': {},
                'lvlbackgrounds': {},
                'server_id': serverid
            }
            db.backgrounds.insert_one(settings)
        bginfo = db.backgrounds.find_one({'server_id': serverid})

        if server.id in self.settings["disabled_servers"]:
            await self.bot.say("Leveler commands for this server are disabled!")
            return

        if not type:
            await self.bot.say("Invalid Background Type. (profile, rank, levelup)\n{}lvlshop list profile".format(ctx.prefix))
            return

        em = discord.Embed(description='', colour=user.colour)
        if type.lower() == "profile":
            em.set_author(name="Profile Backgrounds for {}".format(self.bot.user.name), icon_url = self.bot.user.avatar_url)
            xbgs = bginfo["backgrounds"]
        elif type.lower() == "rank":
            em.set_author(name="Rank Backgrounds for {}".format(self.bot.user.name), icon_url = self.bot.user.avatar_url)
            xbgs = bginfo["rankbackgrounds"]
        elif type.lower() == "levelup":
            em.set_author(name="Level Up Backgrounds for {}".format(self.bot.user.name), icon_url = self.bot.user.avatar_url)
            xbgs = bginfo["lvlbackgrounds"]
        else:
            await self.bot.say("Invalid Background Type. (profile, rank, levelup)\n{}lvlshop list profile".format(ctx.prefix))
            return

        bg_url = []
        for bgname in xbgs.keys():
            bg = xbgs[bgname]
            bg_url.append("[{}]({})".format(bgname, bg["bg_img"]))
        bg_url.remove("[{}]({})".format("default", xbgs["default"]["bg_img"]))
        bg_url.sort()
        bgs = "\n".join(bg_url)

        total_pages = 0
        for page in pagify(bgs):
            total_pages +=1

        counter = 1
        for page in pagify(bgs):
            em.description = page
            em.set_footer(text = "Page {} of {}".format(counter, total_pages))
            await self.bot.say(embed = em)
            counter += 1


    def _bg_convert_dict(self, userinfo):
        if 'backgrounds' not in userinfo or not isinstance(userinfo['backgrounds'], dict):
            def_bg = {
                "background_name": "default",
                "bg_img": "http://i.imgur.com/8T1FUP5.jpg",
                "price": 0,
            }
            def_rbg = {
                "background_name": "default",
                "bg_img": "http://i.imgur.com/SorwIrc.jpg",
                "price": 0,
            }
            def_lbg = {
                "background_name": "default",
                "bg_img": "http://i.imgur.com/eEFfKqa.jpg",
                "price": 0,
            }
            db.users.update_one({'user_id': user.id}, {'$set': {
                "backgrounds.default": def_bg,
                "rankbackgrounds.default": def_rbg,
                "lvlbackgrounds.default": def_lbg,
            }}, upsert=True)
        return db.users.find_one({'user_id': userinfo['user_id']})

    async def draw_profile(self, user, server):
        font_thin_file = 'data/leveler/fonts/Uni_Sans_Thin.ttf'
        font_heavy_file = 'data/leveler/fonts/YasashisaAntique.ttf'
        font_file = 'data/leveler/fonts/YasashisaAntique.ttf'
        font_bold_file = 'data/leveler/fonts/SourceSansPro-Semibold.ttf'

        name_fnt = ImageFont.truetype(font_heavy_file, 22)
        name_u_fnt = ImageFont.truetype(font_unicode_file, 20)
        title_fnt = ImageFont.truetype(font_heavy_file, 15)
        title_u_fnt = ImageFont.truetype(font_unicode_file, 15)
        label_fnt = ImageFont.truetype(font_bold_file, 18)
        exp_fnt = ImageFont.truetype(font_bold_file, 13)
        large_fnt = ImageFont.truetype(font_thin_file, 33)
        rep_fnt = ImageFont.truetype(font_heavy_file, 26)
        rep_u_fnt = ImageFont.truetype(font_unicode_file, 25)
        text_fnt = ImageFont.truetype(font_file, 13)
        text_u_fnt = ImageFont.truetype(font_unicode_file, 14)
        symbol_u_fnt = ImageFont.truetype(font_unicode_file, 15)

        def _write_unicode(text, init_x, y, font, unicode_font, fill):
            write_pos = init_x

            for char in text:
                if char.isalnum() or char in string.punctuation or char in string.whitespace:
                    draw.text((write_pos, y), char, font=font, fill=fill)
                    write_pos += font.getsize(char)[0]
                else:
                    draw.text((write_pos, y), u"{}".format(char), font=unicode_font, fill=fill)
                    write_pos += unicode_font.getsize(char)[0]
        # get urls
        userinfo = db.users.find_one({'user_id':user.id})
        self._badge_convert_dict(userinfo)
        userinfo = db.users.find_one({'user_id':user.id}) ##############################################
        bg_url = userinfo["profile_background"]
        profile_url = user.avatar_url

        # COLORS
        white_color = (240,240,240,255)
        light_color = (160,160,160,255)
        if "rep_color" not in userinfo.keys() or not userinfo["rep_color"]:
            rep_fill = (255,255,255,230)
        else:
            rep_fill = tuple(userinfo["rep_color"])
        # determines badge section color, should be behind the titlebar
        if "badge_col_color" not in userinfo.keys() or not userinfo["badge_col_color"]:
            badge_fill = (128,151,165,230)
        else:
            badge_fill = tuple(userinfo["badge_col_color"])
        if "profile_info_color" in userinfo.keys():
            info_fill = tuple(userinfo["profile_info_color"])
        else:
            info_fill = (30, 30 ,30, 220)
        info_fill_tx = (info_fill[0], info_fill[1], info_fill[2], 150)
        if "profile_exp_color" not in userinfo.keys() or not userinfo["profile_exp_color"]:
            exp_fill = (255, 255, 255, 230)
        else:
            exp_fill = tuple(userinfo["profile_exp_color"])
        if badge_fill == (128,151,165,230):
            level_fill = white_color
        else:
            level_fill = self._contrast(exp_fill, info_fill, badge_fill)

        # create image objects
        bg_image = Image
        profile_image = Image

        async with self.session.get(bg_url) as r:
            image = await r.content.read()
        with open('data/leveler/temp/{}_temp_profile_bg.png'.format(user.id),'wb') as f:
            f.write(image)
        try:
            async with self.session.get(profile_url) as r:
                image = await r.content.read()
        except:
            async with self.session.get(default_avatar_url) as r:
                image = await r.content.read()
        with open('data/leveler/temp/{}_temp_profile_profile.png'.format(user.id),'wb') as f:
            f.write(image)

        #bg_image = Image.open('data/leveler/temp/{}_temp_profile_bg.png'.format(user.id)).convert('RGBA')
        try:
            bg_image = Image.open('data/leveler/temp/{}_temp_profile_bg.png'.format(user.id)).convert('RGBA')
        except:
            image_name = "default"
            uinfo = userinfo['backgrounds'][image_name]
            db.users.update_one({'user_id': userinfo['user_id']}, {'$set': {
                "profile_background": uinfo['bg_img'],
            }})
            await self.bot.say("Profile Background has been reset to default! Please run the Profile command again!")
            return
        profile_image = Image.open('data/leveler/temp/{}_temp_profile_profile.png'.format(user.id)).convert('RGBA')

        # set canvas
        bg_color = (255,255,255,0)
        result = Image.new('RGBA', (340, 390), bg_color)
        process = Image.new('RGBA', (340, 390), bg_color)

        # draw
        draw = ImageDraw.Draw(process)

        # puts in background
        bg_image = bg_image.resize((340, 340), Image.ANTIALIAS)
        bg_image = bg_image.crop((0,0,340, 305))
        result.paste(bg_image,(0,0))

        # draw filter
        draw.rectangle([(0,0),(340, 340)], fill=(0,0,0,10))

        # draw transparent overlay
        vert_pos = 305
        left_pos = 0
        right_pos = 340
        title_height = 30
        gap = 3

        draw.rectangle([(0,134), (340, 325)], fill=info_fill_tx) # general content
        # draw profile circle
        multiplier = 8
        lvl_circle_dia = 116
        circle_left = 14
        circle_top = 48
        raw_length = lvl_circle_dia * multiplier

        # create mask
        mask = Image.new('L', (raw_length, raw_length), 0)
        draw_thumb = ImageDraw.Draw(mask)
        draw_thumb.ellipse((0, 0) + (raw_length, raw_length), fill = 255, outline = 0)

        # border
        lvl_circle = Image.new("RGBA", (raw_length, raw_length))
        draw_lvl_circle = ImageDraw.Draw(lvl_circle)
        draw_lvl_circle.ellipse([0, 0, raw_length, raw_length], fill=(255, 255, 255, 255), outline = (255, 255, 255, 250))
        # put border
        lvl_circle = lvl_circle.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        lvl_bar_mask = mask.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        process.paste(lvl_circle, (circle_left, circle_top), lvl_bar_mask)

        # put in profile picture
        total_gap = 6
        border = int(total_gap/2)
        profile_size = lvl_circle_dia - total_gap
        raw_length = profile_size * multiplier
        output = ImageOps.fit(profile_image, (raw_length, raw_length), centering=(0.5, 0.5))
        output = output.resize((profile_size, profile_size), Image.ANTIALIAS)
        mask = mask.resize((profile_size, profile_size), Image.ANTIALIAS)
        profile_image = profile_image.resize((profile_size, profile_size), Image.ANTIALIAS)
        process.paste(profile_image, (circle_left + border, circle_top + border), mask)

        # write label text
        white_color = (240,240,240,255)
        light_color = (160,160,160,255)
        dark_color = (35, 35, 35, 255)

        head_align = 140
        # determine info text color
        info_text_color = self._contrast(info_fill, white_color, dark_color)
        _write_unicode(self._truncate_text(user.name, 14).upper(), head_align, 142, name_fnt, name_u_fnt, info_text_color) # NAME
        _write_unicode(userinfo["title"].upper(), head_align, 170, title_fnt, title_u_fnt, info_text_color)

        # draw divider
        draw.rectangle([(0,323), (340, 324)], fill=(0,0,0,255)) # box
        # draw text box
        draw.rectangle([(0,324), (340, 390)], fill=(info_fill[0],info_fill[1],info_fill[2],255)) # box

        #rep_text = "{} REP".format(userinfo["rep"])
        rep_text = "{}".format(userinfo["rep"])
        _write_unicode("❤", 10, 9, rep_fnt, rep_u_fnt, rep_fill)#info_text_color)
        _write_unicode(rep_text, 35, 6, rep_fnt, rep_u_fnt, rep_fill)
        #draw.text((self._center(60, 60, rep_text, rep_fnt), 6), rep_text,  font=rep_fnt, fill=rep_fill)#info_text_color) # Exp Text

        lvl_left = 100
        label_align = 362 # vertical
        draw.text((self._center(0, 140, "    RANK", label_fnt), label_align), "    RANK",  font=label_fnt, fill=info_text_color) # Rank
        draw.text((self._center(0, 340, "    LEVEL", label_fnt), label_align), "    LEVEL",  font=label_fnt, fill=info_text_color) # Exp
        draw.text((self._center(200, 340, "BALANCE", label_fnt), label_align), "BALANCE",  font=label_fnt, fill=info_text_color) # Credits

        if "linux" in platform.system().lower():
            global_symbol = u"\U0001F30E "
            fine_adjust = 1
        else:
            global_symbol = "G."
            fine_adjust = 0

        _write_unicode(global_symbol, 36, label_align + 5, label_fnt, symbol_u_fnt, info_text_color) # Symbol
        _write_unicode(global_symbol, 134, label_align + 5, label_fnt, symbol_u_fnt, info_text_color) # Symbol

        # userinfo
        global_rank = "#{}".format(await self._find_global_rank(user))
        global_level = "{}".format(self._find_level(userinfo["total_exp"]))
        draw.text((self._center(0, 140, global_rank, large_fnt), label_align-27), global_rank,  font=large_fnt, fill=info_text_color) # Rank
        draw.text((self._center(0, 340, global_level, large_fnt), label_align-27), global_level,  font=large_fnt, fill=info_text_color) # Exp
        # draw level bar
        exp_font_color = self._contrast(exp_fill, light_color, dark_color)
        exp_frac = int(userinfo["total_exp"] - self._level_exp(int(global_level)))
        exp_total = self._required_exp(int(global_level) + 1)
        bar_length = int(exp_frac/exp_total * 340)
        draw.rectangle([(0, 305), (340, 323)], fill=(level_fill[0],level_fill[1],level_fill[2],245)) # level box
        draw.rectangle([(0, 305), (bar_length, 323)], fill=(exp_fill[0],exp_fill[1],exp_fill[2],255)) # box
        exp_text = "{}/{}".format(exp_frac, exp_total)# Exp
        draw.text((self._center(0, 340, exp_text, exp_fnt), 305), exp_text,  font=exp_fnt, fill=exp_font_color) # Exp Text

        try:
            bank = self.bot.get_cog('Economy').bank
            if bank.account_exists(user):
                #credits = bank.get_balance(user)
                creditz = bank.get_balance(user)
                if creditz > 10000:
                    creditx = creditz / 1000.0
                    creditx = '%.0f' % creditx
                    credits = creditx + "k"
                else:
                    credits = creditz
            else:
                credits = 0
        except:
            credits = 0
        credit_txt = "${}".format(credits)
        draw.text((self._center(200, 340, credit_txt, large_fnt), label_align-27), self._truncate_text(credit_txt, 18),  font=large_fnt, fill=info_text_color) # Credits

        if userinfo["title"] == '':
            offset = 170
        else:
            offset = 195
        margin = 140
        txt_color = self._contrast(info_fill, white_color, dark_color)
        for line in textwrap.wrap(userinfo["info"], width=26):
        # for line in textwrap.wrap('userinfo["info"]', width=200):
            # draw.text((margin, offset), line, font=text_fnt, fill=white_color)
            _write_unicode(line, margin, offset, text_fnt, text_u_fnt, txt_color)
            offset += text_fnt.getsize(line)[1] + 2

        # sort badges
        priority_badges = []

        for badgename in userinfo['badges'].keys():
            badge = userinfo['badges'][badgename]
            priority_num = badge["priority_num"]
            if priority_num != 0 and priority_num != -1:
                priority_badges.append((badge, priority_num))
        sorted_badges = sorted(priority_badges, key=operator.itemgetter(1), reverse=False)

        # TODO: simplify this. it shouldn't be this complicated... sacrifices conciseness for customizability
        if "badge_type" not in self.settings.keys() or self.settings["badge_type"] == "circles":
            # circles require antialiasing
            vert_pos = 172
            right_shift = 0
            left = 9 + right_shift
            right = 52 + right_shift
            size = 38
            total_gap = 4 # /2
            hor_gap = 6
            vert_gap = 6
            border_width = int(total_gap/2)
            multiplier = 6 # for antialiasing
            raw_length = size * multiplier
            mult = [
                (0,0), (1,0), (2,0),
                (0,1), (1,1), (2,1),
                (0,2), (1,2), (2,2)]
            for num in range(9):
                coord = (left + int(mult[num][0])*int(hor_gap+size), vert_pos + int(mult[num][1])*int(vert_gap + size))
                if num < len(sorted_badges[:9]):
                    pair = sorted_badges[num]
                    badge = pair[0]
                    bg_color = badge["bg_img"]
                    border_color = None
                    # draw mask circle
                    mask = Image.new('L', (raw_length, raw_length), 0)
                    draw_thumb = ImageDraw.Draw(mask)
                    draw_thumb.ellipse((0, 0) + (raw_length, raw_length), fill = 255, outline = 0)

                    # determine image or color for badge bg
                    if await self._valid_image_url(bg_color):
                        # get image
                        async with self.session.get(bg_color) as r:
                            image = await r.content.read()
                        with open('data/leveler/temp/{}_temp_badge.png'.format(user.id),'wb') as f:
                            f.write(image)
                        badge_image = Image.open('data/leveler/temp/{}_temp_badge.png'.format(user.id)).convert('RGBA')
                        badge_image = badge_image.resize((raw_length, raw_length), Image.ANTIALIAS)

                        # structured like this because if border = 0, still leaves outline.
                        if border_color:
                            square = Image.new('RGBA', (raw_length, raw_length), border_color)
                            # put border on ellipse/circle
                            output = ImageOps.fit(square, (raw_length, raw_length), centering=(0.5, 0.5))
                            output = output.resize((size, size), Image.ANTIALIAS)
                            outer_mask = mask.resize((size, size), Image.ANTIALIAS)
                            process.paste(output, coord, outer_mask)

                            # put on ellipse/circle
                            output = ImageOps.fit(badge_image, (raw_length, raw_length), centering=(0.5, 0.5))
                            output = output.resize((size - total_gap, size - total_gap), Image.ANTIALIAS)
                            inner_mask = mask.resize((size - total_gap, size - total_gap), Image.ANTIALIAS)
                            process.paste(output, (coord[0] + border_width, coord[1] + border_width), inner_mask)
                        else:
                            # put on ellipse/circle
                            output = ImageOps.fit(badge_image, (raw_length, raw_length), centering=(0.5, 0.5))
                            output = output.resize((size, size), Image.ANTIALIAS)
                            outer_mask = mask.resize((size, size), Image.ANTIALIAS)
                            process.paste(output, coord, outer_mask)
                else:
                    plus_fill = exp_fill
                    # put on ellipse/circle
                    plus_square = Image.new('RGBA', (raw_length, raw_length))
                    plus_draw = ImageDraw.Draw(plus_square)
                    plus_draw.rectangle([(0,0), (raw_length, raw_length)], fill=(info_fill[0],info_fill[1],info_fill[2],245))
                    # draw plus signs
                    margin = 60
                    thickness = 40
                    v_left = int(raw_length/2 - thickness/2)
                    v_right = v_left + thickness
                    v_top = margin
                    v_bottom = raw_length - margin
                    plus_draw.rectangle([(v_left,v_top), (v_right, v_bottom)], fill=(plus_fill[0],plus_fill[1],plus_fill[2],245))
                    h_left = margin
                    h_right = raw_length - margin
                    h_top = int(raw_length/2 - thickness/2)
                    h_bottom = h_top + thickness
                    plus_draw.rectangle([(h_left,h_top), (h_right, h_bottom)], fill=(plus_fill[0],plus_fill[1],plus_fill[2],245))
                    # put border on ellipse/circle
                    output = ImageOps.fit(plus_square, (raw_length, raw_length), centering=(0.5, 0.5))
                    output = output.resize((size, size), Image.ANTIALIAS)
                    outer_mask = mask.resize((size, size), Image.ANTIALIAS)
                    process.paste(output, coord, outer_mask)

                # attempt to remove badge image
                try:
                    os.remove('data/leveler/temp/{}_temp_badge.png'.format(user.id))
                except:
                    pass

        result = Image.alpha_composite(result, process)
        result = self._add_corners(result, 25)
        result.save('data/leveler/temp/{}_profile.png'.format(user.id),'PNG', quality=100)

        # remove images

        os.remove('data/leveler/temp/{}_temp_profile_bg.png'.format(user.id))
        os.remove('data/leveler/temp/{}_temp_profile_profile.png'.format(user.id))


    # returns color that contrasts better in background
    def _contrast(self, bg_color, color1, color2):
        color1_ratio = self._contrast_ratio(bg_color, color1)
        color2_ratio = self._contrast_ratio(bg_color, color2)
        if color1_ratio >= color2_ratio:
            return color1
        else:
            return color2

    def _luminance(self, color):
        # convert to greyscale
        luminance = float((0.2126*color[0]) + (0.7152*color[1]) + (0.0722*color[2]))
        return luminance

    def _contrast_ratio(self, bgcolor, foreground):
        f_lum = float(self._luminance(foreground)+0.05)
        bg_lum = float(self._luminance(bgcolor)+0.05)

        if bg_lum > f_lum:
            return bg_lum/f_lum
        else:
            return f_lum/bg_lum

    # returns a string with possibly a nickname
    def _name(self, user, max_length):
        if user.name == user.display_name:
            return user.name
        else:
            return "{} ({})".format(user.name, self._truncate_text(user.display_name, max_length - len(user.name) - 3), max_length)

    async def _add_dropshadow(self, image, offset=(4,4), background=0x000, shadow=0x0F0, border=3, iterations=5):
        totalWidth = image.size[0] + abs(offset[0]) + 2*border
        totalHeight = image.size[1] + abs(offset[1]) + 2*border
        back = Image.new(image.mode, (totalWidth, totalHeight), background)

        # Place the shadow, taking into account the offset from the image
        shadowLeft = border + max(offset[0], 0)
        shadowTop = border + max(offset[1], 0)
        back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]])

        n = 0
        while n < iterations:
            back = back.filter(ImageFilter.BLUR)
            n += 1

        # Paste the input image onto the shadow backdrop
        imageLeft = border - min(offset[0], 0)
        imageTop = border - min(offset[1], 0)
        back.paste(image, (imageLeft, imageTop))
        return back

    async def draw_rank(self, user, server):
        # fonts
        font_thin_file = 'data/leveler/fonts/Uni_Sans_Thin.ttf'
        font_heavy_file = 'data/leveler/fonts/YasashisaAntique.ttf'
        font_file = 'data/leveler/fonts/YasashisaAntique.ttf'
        font_bold_file = 'data/leveler/fonts/SourceSansPro-Semibold.ttf'

        name_fnt = ImageFont.truetype(font_heavy_file, 20)
        name_u_fnt = ImageFont.truetype(font_unicode_file, 24)
        label_fnt = ImageFont.truetype(font_bold_file, 16)
        exp_fnt = ImageFont.truetype(font_bold_file, 9)
        large_fnt = ImageFont.truetype(font_file, 19)
        large_bold_fnt = ImageFont.truetype(font_bold_file, 24)
        symbol_u_fnt = ImageFont.truetype(font_unicode_file, 15)

        def _write_unicode(text, init_x, y, font, unicode_font, fill):
            write_pos = init_x

            for char in text:
                if char.isalnum() or char in string.punctuation or char in string.whitespace:
                    draw.text((write_pos, y), char, font=font, fill=fill)
                    write_pos += font.getsize(char)[0]
                else:
                    draw.text((write_pos, y), u"{}".format(char), font=unicode_font, fill=fill)
                    write_pos += unicode_font.getsize(char)[0]

        userinfo = db.users.find_one({'user_id':user.id})
        # get urls
        bg_url = userinfo["rank_background"]
        profile_url = user.avatar_url
        server_icon_url = server.icon_url

        # create image objects
        bg_image = Image
        profile_image = Image

        async with self.session.get(bg_url) as r:
            image = await r.content.read()
        with open('data/leveler/temp/test_temp_rank_bg.png'.format(user.id),'wb') as f:
            f.write(image)
        try:
            async with self.session.get(profile_url) as r:
                image = await r.content.read()
        except:
            async with self.session.get(default_avatar_url) as r:
                image = await r.content.read()
        with open('data/leveler/temp/test_temp_rank_profile.png'.format(user.id),'wb') as f:
            f.write(image)
        try:
            async with self.session.get(server_icon_url) as r:
                image = await r.content.read()
        except:
            async with self.session.get(default_avatar_url) as r:
                image = await r.content.read()
        with open('data/leveler/temp/test_temp_server_icon.png'.format(user.id),'wb') as f:
            f.write(image)

        try:
            bg_image = Image.open('data/leveler/temp/test_temp_rank_bg.png'.format(user.id)).convert('RGBA')
        except:
            image_name = "default"
            uinfo = userinfo['rankbackgrounds'][image_name]
            db.users.update_one({'user_id': userinfo['user_id']}, {'$set': {
                "rank_background": uinfo['bg_img'],
            }})
            await self.bot.say("Rank Background has been reset to default! Please run the Rank command again!")
            return
        profile_image = Image.open('data/leveler/temp/test_temp_rank_profile.png'.format(user.id)).convert('RGBA')
        server_image = Image.open('data/leveler/temp/test_temp_server_icon.png'.format(user.id)).convert('RGBA')

        # set canvas
        width = 390
        height = 100
        bg_color = (255,255,255, 0)
        bg_width = width - 50
        result = Image.new('RGBA', (width, height), bg_color)
        process = Image.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(process)

        # info section
        info_section = Image.new('RGBA', (bg_width, height), bg_color)
        info_section_process = Image.new('RGBA', (bg_width, height), bg_color)
        draw_info = ImageDraw.Draw(info_section)
        # puts in background
        bg_image = bg_image.resize((width, height), Image.ANTIALIAS)
        bg_image = bg_image.crop((0,0, width, height))
        info_section.paste(bg_image, (0,0))

        # draw transparent overlays
        draw_overlay = ImageDraw.Draw(info_section_process)
        draw_overlay.rectangle([(0,0), (bg_width,20)], fill=(230,230,230,200))
        draw_overlay.rectangle([(0,20), (bg_width,30)], fill=(120,120,120,180)) # Level bar
        exp_frac = int(userinfo["servers"][server.id]["current_exp"])
        exp_total = self._required_exp(userinfo["servers"][server.id]["level"])
        exp_width = int(bg_width * (exp_frac/exp_total))
        if "rank_info_color" in userinfo.keys():
            exp_color = tuple(userinfo["rank_info_color"])
            exp_color = (exp_color[0], exp_color[1], exp_color[2], 180) # increase transparency
        else:
            exp_color = (140,140,140,230)
        draw_overlay.rectangle([(0,20), (exp_width,30)], fill=exp_color) # Exp bar
        draw_overlay.rectangle([(0,30), (bg_width,31)], fill=(0,0,0,255)) # Divider
        # draw_overlay.rectangle([(0,35), (bg_width,100)], fill=(230,230,230,0)) # title overlay
        for i in range(0,70):
            draw_overlay.rectangle([(0,height-i), (bg_width,height-i)], fill=(20,20,20,255-i*3)) # title overlay

        # draw corners and finalize
        info_section = Image.alpha_composite(info_section, info_section_process)
        info_section = self._add_corners(info_section, 25)
        process.paste(info_section, (35,0))

        # draw level circle
        multiplier = 6
        lvl_circle_dia = 100
        circle_left = 0
        circle_top = int((height- lvl_circle_dia)/2)
        raw_length = lvl_circle_dia * multiplier

        # create mask
        mask = Image.new('L', (raw_length, raw_length), 0)
        draw_thumb = ImageDraw.Draw(mask)
        draw_thumb.ellipse((0, 0) + (raw_length, raw_length), fill = 255, outline = 0)

        # drawing level border
        lvl_circle = Image.new("RGBA", (raw_length, raw_length))
        draw_lvl_circle = ImageDraw.Draw(lvl_circle)
        draw_lvl_circle.ellipse([0, 0, raw_length, raw_length], fill=(250, 250, 250, 250))
        # determines exp bar color
        """
        if "rank_exp_color" not in userinfo.keys() or not userinfo["rank_exp_color"]:
            exp_fill = (255, 255, 255, 230)
        else:
            exp_fill = tuple(userinfo["rank_exp_color"])"""
        exp_fill = (255, 255, 255, 230)

        # put on profile circle background
        lvl_circle = lvl_circle.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        lvl_bar_mask = mask.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        process.paste(lvl_circle, (circle_left, circle_top), lvl_bar_mask)

        # draws mask
        total_gap = 6
        border = int(total_gap/2)
        profile_size = lvl_circle_dia - total_gap
        raw_length = profile_size * multiplier
        # put in profile picture
        output = ImageOps.fit(profile_image, (raw_length, raw_length), centering=(0.5, 0.5))
        output = output.resize((profile_size, profile_size), Image.ANTIALIAS)
        mask = mask.resize((profile_size, profile_size), Image.ANTIALIAS)
        profile_image = profile_image.resize((profile_size, profile_size), Image.ANTIALIAS)
        process.paste(profile_image, (circle_left + border, circle_top + border), mask)

        # draw text
        grey_color = (100,100,100,255)
        white_color = (220,220,220,255)

        # name
        left_text_align = 130
        name_color = 0
        _write_unicode(self._truncate_text(self._name(user, 20), 20), 100, 0, name_fnt, name_u_fnt, grey_color) # Name

        # labels
        v_label_align = 75
        info_text_color = white_color
        draw.text((self._center(100, 200, "  RANK", label_fnt), v_label_align), "  RANK",  font=label_fnt, fill=info_text_color) # Rank
        draw.text((self._center(100, 360, "  LEVEL", label_fnt), v_label_align), "  LEVEL",  font=label_fnt, fill=info_text_color) # Rank
        draw.text((self._center(260, 360, "BALANCE", label_fnt), v_label_align), "BALANCE",  font=label_fnt, fill=info_text_color) # Rank
        local_symbol = u"\U0001F3E0 "
        if "linux" in platform.system().lower():
            local_symbol = u"\U0001F3E0 "
        else:
            local_symbol = "S. "
        _write_unicode(local_symbol, 117, v_label_align + 4, label_fnt, symbol_u_fnt, info_text_color) # Symbol
        _write_unicode(local_symbol, 195, v_label_align + 4, label_fnt, symbol_u_fnt, info_text_color) # Symbol

        # userinfo
        server_rank = "#{}".format(await self._find_server_rank(user, server))
        draw.text((self._center(100, 200, server_rank, large_fnt), v_label_align - 30), server_rank,  font=large_fnt, fill=info_text_color) # Rank
        level_text = "{}".format(userinfo["servers"][server.id]["level"])
        draw.text((self._center(95, 360, level_text, large_fnt), v_label_align - 30), level_text,  font=large_fnt, fill=info_text_color) # Level
        try:
            bank = self.bot.get_cog('Economy').bank
            if bank.account_exists(user):
                #credits = bank.get_balance(user)
                creditz = bank.get_balance(user)
                if creditz > 10000:
                    creditx = creditz / 1000.0
                    creditx = '%.0f' % creditx
                    credits = creditx + "k"
                else:
                    credits = creditz
            else:
                credits = 0
        except:
            credits = 0
        credit_txt = "${}".format(credits)
        draw.text((self._center(260, 360, credit_txt, large_fnt), v_label_align - 30), credit_txt,  font=large_fnt, fill=info_text_color) # Balance
        exp_text = "{}/{}".format(exp_frac, exp_total)
        draw.text((self._center(80, 360, exp_text, exp_fnt), 19), exp_text,  font=exp_fnt, fill=info_text_color) # Rank


        result = Image.alpha_composite(result, process)
        result.save('data/leveler/temp/{}_rank.png'.format(user.id),'PNG', quality=100)

        os.remove('data/leveler/temp/test_temp_rank_bg.png')
        os.remove('data/leveler/temp/test_temp_rank_profile.png')
        os.remove('data/leveler/temp/test_temp_server_icon.png')

    def _add_corners(self, im, rad, multiplier = 6):
        raw_length = rad * 2 * multiplier
        circle = Image.new('L', (raw_length, raw_length), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, raw_length, raw_length), fill=255)
        circle = circle.resize((rad * 2, rad * 2), Image.ANTIALIAS)

        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im


    async def draw_levelup(self, user, server):
        # fonts
        font_thin_file = 'data/leveler/fonts/SourceSansPro-Regular.ttf'
        level_fnt = ImageFont.truetype(font_thin_file, 23)

        userinfo = db.users.find_one({'user_id':user.id})

        # get urls
        bg_url = userinfo["levelup_background"]
        profile_url = user.avatar_url

        # create image objects
        bg_image = Image
        profile_image = Image

        async with self.session.get(bg_url) as r:
            image = await r.content.read()
        with open('data/leveler/temp/{}_temp_level_bg.png'.format(user.id),'wb') as f:
            f.write(image)
        try:
            async with self.session.get(profile_url) as r:
                image = await r.content.read()
        except:
            async with self.session.get(default_avatar_url) as r:
                image = await r.content.read()
        with open('data/leveler/temp/{}_temp_level_profile.png'.format(user.id),'wb') as f:
            f.write(image)

        try:
            bg_image = Image.open('data/leveler/temp/{}_temp_level_bg.png'.format(user.id)).convert('RGBA')
        except:
            image_name = "default"
            uinfo = userinfo['lvlbackgrounds'][image_name]
            db.users.update_one({'user_id': userinfo['user_id']}, {'$set': {
                "levelup_background": uinfo['bg_img'],
            }})
            await self.bot.say("Level-up Background has been reset to default!")
            return
        profile_image = Image.open('data/leveler/temp/{}_temp_level_profile.png'.format(user.id)).convert('RGBA')

        # set canvas
        width = 176
        height = 67
        bg_color = (255,255,255, 0)
        result = Image.new('RGBA', (width, height), bg_color)
        process = Image.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(process)

        # puts in background
        bg_image = bg_image.resize((width, height), Image.ANTIALIAS)
        bg_image = bg_image.crop((0,0, width, height))
        result.paste(bg_image, (0,0))

        # info section
        lvl_circle_dia = 60
        total_gap = 2
        border = int(total_gap/2)
        info_section = Image.new('RGBA', (165, 55), (230,230,230,20))
        info_section = self._add_corners(info_section, int(lvl_circle_dia/2))
        process.paste(info_section, (border,border))

        # draw transparent overlay
        if "levelup_info_color" in userinfo.keys():
            info_color = tuple(userinfo["levelup_info_color"])
            info_color = (info_color[0], info_color[1], info_color[2], 150) # increase transparency
        else:
            info_color = (30, 30 ,30, 150)

        for i in range(0,height):
            draw.rectangle([(0,height-i), (width,height-i)], fill=(info_color[0],info_color[1],info_color[2],255-i*3)) # title overlay

        # draw circle
        multiplier = 6
        circle_left = 4
        circle_top = int((height- lvl_circle_dia)/2)
        raw_length = lvl_circle_dia * multiplier
        # create mask
        mask = Image.new('L', (raw_length, raw_length), 0)
        draw_thumb = ImageDraw.Draw(mask)
        draw_thumb.ellipse((0, 0) + (raw_length, raw_length), fill = 255, outline = 0)

        # border
        lvl_circle = Image.new("RGBA", (raw_length, raw_length))
        draw_lvl_circle = ImageDraw.Draw(lvl_circle)
        draw_lvl_circle.ellipse([0, 0, raw_length, raw_length], fill=(250, 250, 250, 180))
        lvl_circle = lvl_circle.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        lvl_bar_mask = mask.resize((lvl_circle_dia, lvl_circle_dia), Image.ANTIALIAS)
        process.paste(lvl_circle, (circle_left, circle_top), lvl_bar_mask)

        profile_size = lvl_circle_dia - total_gap
        raw_length = profile_size * multiplier
        # put in profile picture
        output = ImageOps.fit(profile_image, (raw_length, raw_length), centering=(0.5, 0.5))
        output = output.resize((profile_size, profile_size), Image.ANTIALIAS)
        mask = mask.resize((profile_size, profile_size), Image.ANTIALIAS)
        profile_image = profile_image.resize((profile_size, profile_size), Image.ANTIALIAS)
        process.paste(profile_image, (circle_left + border, circle_top + border), mask)

        # write label text
        white_text = (250,250,250,255)
        dark_text = (35, 35, 35, 230)
        level_up_text = self._contrast(info_color, white_text, dark_text)
        lvl_text = "LEVEL {}".format(userinfo["servers"][server.id]["level"])
        draw.text((self._center(60, 170, lvl_text, level_fnt), 18), lvl_text, font=level_fnt, fill=level_up_text) # Level Number

        result = Image.alpha_composite(result, process)
        result = self._add_corners(result, int(height/2))
        filename = 'data/leveler/temp/{}_level.png'.format(user.id)
        result.save(filename,'PNG', quality=100)

    async def _handle_on_message(self, message):
        #try:
        server = message.server
        if message.content.lower().startswith("{}".format(prefix)):
            try:
                if message.content.lower().startswith("{}".format(pref[server.id]['PREFIXES'])):
                    return
            except:
                pass
            return
        else:
            text = message.content
            channel = message.channel
            server = message.server
            user = message.author
            # creates user if doesn't exist, bots are not logged.
            await self._create_user(user, server)
            curr_time = time.time()
            userinfo = db.users.find_one({'user_id':user.id})

            if not server or server.id in self.settings["disabled_servers"]:
                return
            if user.bot:
                return

            # check if chat_block exists
            if "chat_block" not in userinfo:
                userinfo["chat_block"] = 0

            if float(curr_time) - float(userinfo["chat_block"]) >= 120 and not any(text.startswith(x) for x in prefix):
                channeldb = db.channels.find_one({'server_id': server.id})
                if channeldb:
                    chan = channeldb['channels']
                    if channel.id in chan.keys():
                        return
                    else:
                        pass
                await self._process_exp(message, userinfo, random.randint(15, 20))
                await self._give_chat_credit(user, server)


    async def _process_exp(self, message, userinfo, exp:int):
        server = message.author.server
        channel = message.channel
        user = message.author  # add to total exp

        required = self._required_exp(userinfo["servers"][server.id]["level"])
        if userinfo["servers"][server.id]["current_exp"] + exp >= required:
            userinfo["servers"][server.id]["level"] += 1
            db.users.update_one({'user_id': user.id}, {'$set': {
                "servers.{}.level".format(server.id): userinfo["servers"][server.id]["level"],
                "servers.{}.current_exp".format(server.id): userinfo["servers"][server.id]["current_exp"] + exp - required,
                "chat_block": time.time(),
                "total_exp": userinfo["total_exp"] + exp  # add to total exp
                }})
            await self._handle_levelup(user, userinfo, server, channel)
        else:
            db.users.update_one({'user_id': user.id}, {'$set': {
                "servers.{}.current_exp".format(server.id): userinfo["servers"][server.id]["current_exp"] + exp,
                "total_exp": userinfo["total_exp"] + exp,  # add to total exp
                "chat_block": time.time()
                }})

    async def _handle_levelup(self, user, userinfo, server, channel):
        if not isinstance(self.settings["lvl_msg"], list):
            self.settings["lvl_msg"] = []
            fileIO("data/leveler/settings.json", "save", self.settings)

        if server.id in self.settings["lvl_msg"]: # if lvl msg is enabled
            # channel lock implementation
            if "lvl_msg_lock" in self.settings.keys() and server.id in self.settings["lvl_msg_lock"].keys():
                channel_id = self.settings["lvl_msg_lock"][server.id]
                channel = find(lambda m: m.id == channel_id, server.channels)

            server_identifier = "" # super hacky
            name = self._is_mention(user) # also super hacky
            # private message takes precedent, of course
            if "private_lvl_msg" in self.settings and server.id in self.settings["private_lvl_msg"]:
                server_identifier = " on {}".format(server.name)
                channel = user
                name = "You"

            new_level = str(userinfo["servers"][server.id]["level"])
            # add to appropriate role if necessary
            try:
                server_roles = db.roles.find_one({'server_id':server.id})
                if server_roles != None:
                    for role in server_roles['roles'].keys():
                        if int(server_roles['roles'][role]['level']) == int(new_level):
                            if server_roles['roles'][role]['remove_role'] != None:
                                remove_role_obj = discord.utils.find(
                                    lambda r: r.name == server_roles['roles'][role]['remove_role'], server.roles)
                                if remove_role_obj != None:
                                    await self.bot.remove_roles(user, remove_role_obj)
                            await asyncio.sleep(1)
                            role_obj = discord.utils.find(lambda r: r.name == role, server.roles)
                            await self.bot.add_roles(user, role_obj)
            except:
                await self.bot.send_message(channel, 'Role was not set. Missing Permissions!')

            # add appropriate badge if necessary
            try:
                server_linked_badges = db.badgelinks.find_one({'server_id':server.id})
                if server_linked_badges != None:
                    for badge_name in server_linked_badges['badges']:
                        if int(server_linked_badges['badges'][badge_name]) == int(new_level):
                            server_badges = db.badges.find_one({'server_id':server.id})
                            if server_badges != None and badge_name in server_badges['badges'].keys():
                                userinfo_db = db.users.find_one({'user_id':user.id})
                                new_badge_name = "{}_{}".format(badge_name, server.id)
                                userinfo_db["badges"][new_badge_name] = server_badges['badges'][badge_name]
                                db.users.update_one({'user_id':user.id}, {'$set':{"badges": userinfo_db["badges"]}})
            except:
                await self.bot.send_message(channel, 'Error. Badge was not given!')

            if "text_only" in self.settings and server.id in self.settings["text_only"]:
                await self.bot.send_typing(channel)
                em = discord.Embed(description='**{} just gained a level{}! (LEVEL {})**'.format(name, server_identifier, new_level), colour=user.colour)
                await self.bot.send_message(channel, '', embed = em)
            else:
                await self.draw_levelup(user, server)
                await self.bot.send_typing(channel)
                try:
                    await self.bot.send_file(channel, 'data/leveler/temp/{}_level.png'.format(user.id), content='**{} just gained a level{}!**'.format(name, server_identifier))
                    os.remove('data/leveler/temp/{}_level.png'.format(user.id))
                    os.remove('data/leveler/temp/{}_temp_level_bg.png'.format(user.id))
                    os.remove('data/leveler/temp/{}_temp_level_profile.png'.format(user.id))
                except:
                    em = discord.Embed(description='**{} just gained a level{}! (LEVEL {})**'.format(name, server_identifier,
                                                                                      new_level), colour=user.colour)
                    await self.bot.send_message(channel, '', embed=em)
        else:
            if "lvl_msg_lock" in self.settings.keys() and server.id in self.settings["lvl_msg_lock"].keys():
                channel_id = self.settings["lvl_msg_lock"][server.id]
                channel = find(lambda m: m.id == channel_id, server.channels)

            server_identifier = ""  # super hacky
            # name = self._is_mention(user) # also super hacky
            # private message takes precedent, of course
            if "private_lvl_msg" in self.settings and server.id in self.settings["private_lvl_msg"]:
                server_identifier = " on {}".format(server.name)
                channel = user
                name = "You"

            new_level = str(userinfo["servers"][server.id]["level"])
            # add to appropriate role if necessary
            try:
                server_roles = db.roles.find_one({'server_id': server.id})
                if server_roles != None:
                    for role in server_roles['roles'].keys():
                        if int(server_roles['roles'][role]['level']) == int(new_level):
                            role_obj = discord.utils.find(lambda r: r.name == role, server.roles)
                            await self.bot.add_roles(user, role_obj)
                            await self.bot.send_message(channel, "{0}, you obtained the role **{1}** for reaching level **{2}**!".format(user.mention, role_obj, new_level))
                            try:
                                await self.bot.add_roles(user, role_obj)
                            except:
                                pass

                            if server_roles['roles'][role]['remove_role'] != None:
                                remove_role_obj = discord.utils.find(
                                    lambda r: r.name == server_roles['roles'][role]['remove_role'], server.roles)
                                if remove_role_obj != None:
                                    await self.bot.remove_roles(user, remove_role_obj)
            except:
                await self.bot.send_message(channel, 'Role was not set. Missing Permissions!')

            # add appropriate badge if necessary
            try:
                server_linked_badges = db.badgelinks.find_one({'server_id': server.id})
                if server_linked_badges != None:
                    for badge_name in server_linked_badges['badges']:
                        if int(server_linked_badges['badges'][badge_name]) == int(new_level):
                            server_badges = db.badges.find_one({'server_id': server.id})
                            if server_badges != None and badge_name in server_badges['badges'].keys():
                                userinfo_db = db.users.find_one({'user_id': user.id})
                                new_badge_name = "{}_{}".format(badge_name, server.id)
                                userinfo_db["badges"][new_badge_name] = server_badges['badges'][badge_name]
                                db.users.update_one({'user_id': user.id}, {'$set': {"badges": userinfo_db["badges"]}})
            except:
                await self.bot.send_message(channel, 'Error. Badge was not given!')


    async def _find_server_rank(self, user, server):
        targetid = user.id
        users = []

        for userinfo in db.users.find({}):
            try:
                server_exp = 0
                userid = userinfo["user_id"]
                for i in range(userinfo["servers"][server.id]["level"]):
                    server_exp += self._required_exp(i)
                server_exp += userinfo["servers"][server.id]["current_exp"]
                users.append((userid, server_exp))
            except:
                pass

        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)

        rank = 1
        for a_user in sorted_list:
            if a_user[0] == targetid:
                return rank
            rank+=1

    async def _find_server_rep_rank(self, user, server):
        targetid = user.id
        users = []
        for userinfo in db.users.find({}):
            userid = userinfo["user_id"]
            if "servers" in userinfo and server.id in userinfo["servers"]:
                users.append((userinfo["user_id"], userinfo["rep"]))

        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)

        rank = 1
        for a_user in sorted_list:
            if a_user[0] == targetid:
                return rank
            rank+=1

    async def _find_server_exp(self, user, server):
        server_exp = 0
        userinfo = db.users.find_one({'user_id':user.id})

        try:
            for i in range(userinfo["servers"][server.id]["level"]):
                server_exp += self._required_exp(i)
            server_exp +=  userinfo["servers"][server.id]["current_exp"]
            return server_exp
        except:
            return server_exp

    async def _find_global_rank(self, user):
        users = []

        for userinfo in db.users.find({}):
            try:
                userid = userinfo["user_id"]
                users.append((userid, userinfo["total_exp"]))
            except KeyError:
                pass
        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)

        rank = 1
        for stats in sorted_list:
            if stats[0] == user.id:
                return rank
            rank+=1

    async def _find_global_rep_rank(self, user):
        users = []

        for userinfo in db.users.find({}):
            try:
                userid = userinfo["user_id"]
                users.append((userid, userinfo["rep"]))
            except KeyError:
                pass
        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)

        rank = 1
        for stats in sorted_list:
            if stats[0] == user.id:
                return rank
            rank+=1

    # handles user creation, adding new server, blocking
    async def _create_user(self, user, server):
        try:
            userinfo = db.users.find_one({'user_id':user.id})
            if not userinfo:
                new_account = {
                    "user_id" : user.id,
                    "username" : user.name,
                    "servers": {},
                    "total_exp": 0,
                    "profile_background": "http://i.imgur.com/8T1FUP5.jpg",
                    "rank_background": "http://i.imgur.com/SorwIrc.jpg",
                    "levelup_background": "http://i.imgur.com/eEFfKqa.jpg",
                    "title": "",
                    "info": "I am a mysterious person.",
                    "rep": 0,
                    "badges":{},
                    "active_badges":{},
                    "rep_color": [],
                    "badge_col_color": [],
                    "rep_block": 0,
                    "chat_block": 0,
                    "profile_block": 0,
                    "rank_block": 0
                }
                db.users.insert_one(new_account)

            userinfo = db.users.find_one({'user_id':user.id})

            if "username" not in userinfo or userinfo["username"] != user.name:
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "username": user.name,
                    }}, upsert = True)

            if "servers" not in userinfo or server.id not in userinfo["servers"]:
                db.users.update_one({'user_id':user.id}, {'$set':{
                        "servers.{}.level".format(server.id): 0,
                        "servers.{}.current_exp".format(server.id): 0,
                    }}, upsert = True)
            if "backgrounds" not in userinfo:
                def_bg = {
                        "background_name": "default",
                        "bg_img": "http://i.imgur.com/8T1FUP5.jpg",
                        "price": 0,
                    }
                def_rbg = {
                        "background_name": "default",
                        "bg_img": "http://i.imgur.com/SorwIrc.jpg",
                        "price": 0,
                    }
                def_lbg = {
                        "background_name": "default",
                        "bg_img": "http://i.imgur.com/eEFfKqa.jpg",
                        "price": 0,
                    }
                db.users.update_one({'user_id': user.id}, {'$set': {
                    "backgrounds.default": def_bg,#.{}".format("default"): {},
                    "rankbackgrounds.default": def_rbg,
                    "lvlbackgrounds.default": def_lbg,
                }}, upsert=True)
        except AttributeError as e:
            pass

    def _truncate_text(self, text, max_length):
        if len(text) > max_length:
            try:
                if text.strip('$').isdigit():
                    text = int(text.strip('$'))
                    return "${:.2E}".format(text)
            except:
                pass
            return text[:max_length-3] + "..."
        return text

    # finds the the pixel to center the text
    def _center(self, start, end, text, font):
        dist = end - start
        width = font.getsize(text)[0]
        start_pos = start + ((dist-width)/2)
        return int(start_pos)

    # calculates required exp for next level
    def _required_exp(self, level:int):
        if level < 0:
            return 0
        return 139*level+65

    def _level_exp(self, level: int):
        return level*65 + 139*level*(level-1)//2

    def _find_level(self, total_exp):
        # this is specific to the function above
        return int((1/278)*(9 + math.sqrt(81 + 1112*(total_exp))))

# ------------------------------ setup ----------------------------------------
def check_folders():
    if not os.path.exists("data/leveler"):
        print("Creating data/leveler folder...")
        os.makedirs("data/leveler")

    if not os.path.exists("data/leveler/temp"):
        print("Creating data/leveler/temp folder...")
        os.makedirs("data/leveler/temp")

def transfer_info():
    try:
        users = fileIO("data/leveler/users.json", "load")
        for user_id in users:
            os.makedirs("data/leveler/users/{}".format(user_id))
            # create info.json
            f = "data/leveler/users/{}/info.json".format(user_id)
            if not fileIO(f, "check"):
                fileIO(f, "save", users[user_id])
    except:
        pass

def check_files():
    default = {
        "bg_price": 0,
        "lvl_msg": [], # enabled lvl msg servers
        "disabled_servers": [],
        "badge_type": "circles",
        "mention" : True,
        "text_only": [],
        "server_roles": {},
        "rep_cooldown": 86400,
        "chat_cooldown": 120
        }

    settings_path = "data/leveler/settings.json"
    if not os.path.isfile(settings_path):
        print("Creating default leveler settings.json...")
        fileIO(settings_path, "save", default)

    bgs = {
            "profile": {
                "alice": "http://i.imgur.com/MUSuMao.png",
                "bluestairs": "http://i.imgur.com/EjuvxjT.png",
                "lamp": "http://i.imgur.com/0nQSmKX.jpg",
                "coastline": "http://i.imgur.com/XzUtY47.jpg",
                "redblack": "http://i.imgur.com/74J2zZn.jpg",
                "default": "http://i.imgur.com/8T1FUP5.jpg",
                "iceberg": "http://i.imgur.com/8KowiMh.png",
                "miraiglasses": "http://i.imgur.com/2Ak5VG3.png",
                "miraikuriyama": "http://i.imgur.com/jQ4s4jj.png",
                "mountaindawn": "http://i.imgur.com/kJ1yYY6.jpg",
                "waterlilies": "http://i.imgur.com/qwdcJjI.jpg",
                "greenery": "http://i.imgur.com/70ZH6LX.png"
            },
            "rank": {
                "aurora" : "http://i.imgur.com/gVSbmYj.jpg",
                "default" : "http://i.imgur.com/SorwIrc.jpg",
                "nebula": "http://i.imgur.com/V5zSCmO.jpg",
                "mountain" : "http://i.imgur.com/qYqEUYp.jpg",
                "abstract" : "http://i.imgur.com/70ZH6LX.png",
                "city": "http://i.imgur.com/yr2cUM9.jpg",
            },
            "levelup": {
                "default" : "http://i.imgur.com/eEFfKqa.jpg",
            },
        }

    bgs_path = "data/leveler/backgrounds.json"
    if not os.path.isfile(bgs_path):
        print("Creating default leveler backgrounds.json...")
        fileIO(bgs_path, "save", bgs)

    f = "data/leveler/badges.json"
    if not fileIO(f, "check"):
        print("Creating badges.json...")
        fileIO(f, "save", {})

    fd = "data/leveler/channels.json"
    if not fileIO(fd, "check"):
        print("Creating channels.json...")
        fileIO(fd, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Leveler(bot)
    bot.add_listener(n._handle_on_message, "on_message")
    bot.add_cog(n)
