######### TRIVIA #########
import discord
from discord.ext import commands
import random
import time
import json


waifus=json.loads(open("waifus.json").read())
waifus=sorted(waifus, key=lambda w: w["likes"]+w["trash"])

channel_used_whoisthiswaifu = {}
channel_used_waifufromwhatanimu = {}
class trivia:
	def __init__(self, client):
		self.client = client
		
		
		
	##### WHO IS THIS WAIFU? #####
	@commands.command(pass_context=True)
	async def waifu(self, ctx, dif : str = "m"):
		if dif == "e":
			waifus2cuck=waifus[-100:]
		elif dif == "m":
			waifus2cuck=waifus[-1000:]
		elif dif == "h":
			waifus2cuck=waifus[-8000:]
		elif dif == "suicide":
			waifus2cuck=waifus
		channel = ctx.message.channel
		author = ctx.message.author
		print(dif)
		if not channel.id in channel_used_whoisthiswaifu:
			channel_used_whoisthiswaifu[channel.id] = True
		else:
			if channel_used_whoisthiswaifu[channel.id] == True:
				await self.client.say("You are already playing Who Is This Waifu, don't rush it.")
				return
			else:
				channel_used_whoisthiswaifu[channel.id] = True
		
		while True:
			waifu=waifus2cuck[random.randint(0, len(waifus2cuck)-1)]
			
			waifuName = waifu['name']
			waifuImg = waifu['display_picture']
			
			await self.client.say("**Who Is This Waifu?**")
			await self.client.say("*Type the complete name of the waifu. Everyone in the channel can participate. Yay!*")
			
			await self.client.send_file(channel, waifuImg)
			
		
			await self.client.say("Type `next` for another waifu (accessible by %s). \nType `stop` to end the cmd (accessible by %s)" % (author, author))
			
		
			
			start = time.time()
			
			while time.time()<(start+60):
				print("inside while")
				m = await self.client.wait_for_message(channel=channel, timeout=1)
				print("pepe")
				if time.time()>=(start+60):
					await self.client.say("Oops! Nobody got it right. The name of the waifu is %s." % (waifuName))
					channel_used_whoisthiswaifu[channel.id] = False
					return
				if m is None:
					continue
				if (m.content).lower() ==(waifuName).lower():
					await self.client.say("Nice job! %s guessed the name right! The answer was %s" % (m.author, waifuName))
					break
				if m.content == "next" and m.author == author:
					break
				if m.content == "stop" and m.author == author:
					await self.client.say("%s has stopped *Who Is This Waifu?*" % (author)) 
					channel_used_whoisthiswaifu[channel.id] = False
					return
		channel_used_whoisthiswaifu[channel.id] = False
		
		
		
		##### WAIFU FROM WHAT ANIMU? #####
	@commands.command(pass_context=True)
	async def waifufromwhatanimu(self, ctx, dif : str = "m"):
		if dif == "e":
			waifus2cuck=waifus[-100:]
		elif dif == "m":
			waifus2cuck=waifus[-1000:]
		elif dif == "h":
			waifus2cuck=waifus[-8000:]
		elif dif == "suicide":
			waifus2cuck=waifus
		channel = ctx.message.channel
		author = ctx.message.author
		print(dif)
		if not channel.id in channel_used_waifufromwhatanimu:
			channel_used_waifufromwhatanimu[channel.id] = True
		else:
			if channel_used_waifufromwhatanimu[channel.id] == True:
				await self.client.say("You are already playing Waifu From What Animu, don't rush it.")
				return
			else:
				channel_used_waifufromwhatanimu[channel.id] = True
		
		while True:
			waifu=waifus2cuck[random.randint(0, len(waifus2cuck)-1)]
			
			animeName = waifu['series']['name']
			waifuImg = waifu['display_picture']
			
			await self.client.say("**Waifu From What Animu?**")
			await self.client.say("*Type the name of the Anime/Series/Game of this waifu. Everyone in the channel can participate. Yay!*")
			
			await self.client.send_file(channel, waifuImg)
			
		
			await self.client.say("Type `next` for another animu (accessible by %s). \nType `stop` to end the cmd (accessible by %s)" % (author, author))
			
		
			
			start = time.time()
			
			while time.time()<(start+60):
				print("inside while")
				m = await self.client.wait_for_message(channel=channel, timeout=1)
				print("pepe")
				if time.time()>=(start+60):
					await self.client.say("Oops! Nobody got it right. The name of the animu is %s." % (animeName))
					channel_used_waifufromwhatanimu[channel.id] = False
					return
				if m is None:
					continue
				if (m.content).lower() ==(animeName).lower():
					await self.client.say("Nice job! %s guessed the name right! The answer was %s" % (m.author, animeName))
					break
				if m.content == "next" and m.author == author:
					break
				if m.content == "stop" and m.author == author:
					await self.client.say("%s has stopped *Waifu From What Animu?*" % (author)) 
					channel_used_waifufromwhatanimu[channel.id] = False
					return
		channel_used_waifufromwhatanimu[channel.id] = False
		
		
def setup(client):
	client.add_cog(trivia(client))
	
