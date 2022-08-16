import discord
from discord.ext import commands
from replit import db
import asyncio

code_leak_msg = discord.Embed(title= "__**CODE  LEAK**__", description="------------------------------", color=0x05ffac)

code_leak_id = 0

code_request_ch_id = 803677123680141312
queue_up_ch_id = 829214996226899999
log_ch_id = 803883330814738442
scrim_chat_ch_id = 916815888244670515

class ScrimHost(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Scrim Module Ready")

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if(user == self.client.user):
			return

		if(reaction.message.channel.id == code_request_ch_id):
			global code_leak_id
			queue_up_channel = self.client.get_channel(queue_up_ch_id)

			if(reaction.emoji == "🟩"):
				await reaction.message.clear_reactions()
				await reaction.message.channel.send("Code confirmed")
				
				await get_queued_player_list(self)

				queue_msg = discord.Embed(title="__**QUEUE UP**__", description="Please click on the raised hand below [✋] to queue up for the code. \nThe code will be sent to you. **Check your DM**", color=0x14fffb)
				queue_msg.set_footer(text="Made with ❤ by sarwin")
				
				await queue_up_channel.purge(limit=10)

				notification_role = reaction.message.guild.get_role(835796429825376257)
				await queue_up_channel.send(notification_role.mention)

				queue_msg = await queue_up_channel.send(embed=queue_msg)
				await queue_msg.add_reaction("✋")
				
				scrim_chat_ch = self.client.get_channel(scrim_chat_ch_id)
				await scrim_chat_ch.send("{} check <#829214996226899999> to get the game code".format(notification_role.mention))

				code_leak_id = 0

			if(reaction.emoji == "🟥"):
				await reaction.message.clear_reactions()
				code_leak_msg.clear_fields()
				await reaction.message.channel.send("Code cancelled")

				code_leak_id = 0	

		#message the code
		if(reaction.message.channel.id == queue_up_ch_id):
			repeated_user = 0
			try:
				repeated_user = db[str(user.id)][0]
			except:
				repeated_user = 0

			if(reaction.emoji == "✋" and repeated_user == 0):
				dm_temp_ch = user.dm_channel
				if(dm_temp_ch == None):
					dm_temp_ch = await user.create_dm()
				
				try:
					await dm_temp_ch.send(embed=code_leak_msg)
					db[str(user.id)] = [1, user.name]
				except:
					error_msg = await reaction.message.channel.send("{} your DM is **inaccessible**\nUnblock the bot _or/and_ set your DM to public then try again in **15** seconds".format(user.mention))
					db[str(user.id)] = [2, user.name]
					await asyncio.sleep(15)
					await error_msg.delete()
					del db[str(user.id)]
					

	#scrim command⠀

	@commands.command()
	async def scrim(self, ctx, game_code, game_mode, region = "Asia"):
		if(ctx.channel.id != code_request_ch_id):
			return

		global code_leak_id

		if(code_leak_id != 0):
			await ctx.send("There is a code leak request in progress.")
			return
	

		code_leak_msg.clear_fields()
		code_leak_msg.add_field(name="GAME CODE", value=game_code, inline=True)
		code_leak_msg.add_field(name="GAME MODE", value=game_mode, inline=True)
		#code_leak_msg.add_field(name="GAME INDEX", value=game_no, inline=True)
		code_leak_msg.add_field(name="SERVER", value=region, inline=True)

		code_leak_msg.add_field(name="NOTE", value="Please review the rules while waiting in queue [#📖-scrims-rule]", inline=False)
		code_leak_msg.set_footer(text="Made with ❤ by sarwin . #RespectRules")

		code_leak_ref = await ctx.send(embed=code_leak_msg)
		await code_leak_ref.add_reaction("🟩")
		await code_leak_ref.add_reaction("🟥")

		code_leak_id = code_leak_ref.id

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		print(error)

async def get_queued_player_list(self):
	queued_players = "**Players who viewed the code:**\n"
	users_id = db.keys()
	for id in users_id: 
		try:
			if(db[str(id)][0] == 1):
				queued_players += "- `{}` \n".format(db[str(id)][1])
				
			del db[str(id)]
		except:
			pass
				
	log_ch = self.client.get_channel(log_ch_id)
	await log_ch.send(queued_players)

def setup(client):
	client.add_cog(ScrimHost(client))