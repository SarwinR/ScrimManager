import discord
from discord.ext import commands
import asyncio

from replit import db
import database_access as fb
from datetime import datetime, timedelta

winRequestPlayerID = None
response = None

winner_tag_ch_id = 803585516095799332

leaderboard_cooldown = False

class WinCounter(commands.Cog):

	def __init__(self, client):
		self.client = client
		#db["scrim_index"]= -1

	@commands.Cog.listener()
	async def on_ready(self):
		print("WinCounter Module Ready")

	@commands.Cog.listener()
	async def on_message(self, message):
		if(message.author == self.client.user):
			return

		global response
		if(message.author.id == winRequestPlayerID):
			if(message.content.lower() == 'yes'):
				response = True
			
			if(message.content.lower() == 'no'):
				response = False	

	@commands.command()
	async def leaderboard(self, ctx, game_mode:str=None):
		if(game_mode == None):
			await ctx.reply("`.leaderboard <gamemode> | gamemode : s/d/t/tournamant`")
			return

		if(game_mode.lower() in ['s', 'd', 't', 'tournament']):
			await arrange_leaderboard(self, ctx, game_mode)
		else:
			await ctx.reply("Please select a valid gamemode s/d/t/tournamant")

	@commands.has_permissions(administrator=True)
	@commands.command()
	async def leaderboard_admin(self, ctx, game_mode:str=None):
		if(game_mode == None):
			await ctx.reply("`.leaderboard_admin <gamemode> | gamemode : s/d/t/tournamant`")
			return

		if(game_mode.lower() in ['s', 'd', 't', 'tournament']):
			await arrange_leaderboard_admin(self, ctx, game_mode)
		else:
			await ctx.reply("Please select a valid gamemode s/d/t/tournamant")

	@commands.has_permissions(administrator=True)
	@commands.command()
	async def removewin(self, ctx, amount:int, game_mode, player_1:discord.Member):
		global winRequestPlayerID
		if(winRequestPlayerID != None):
			await ctx.reply("```❗ [ON GOING PROCESS]```")
		else:
			if(game_mode.lower() in ['s', 'd', 't', 'tournament']):
				winRequestPlayerID = ctx.author.id
				await remove_win(self, ctx, amount, game_mode, player_1)
			else:
				await ctx.reply("Please select a valid gamemode s/d/t/tournamant")
				
	
	#@commands.has_permissions(administrator=True)
	@commands.command()
	async def winner(self, ctx, game_mode, player_1:discord.Member, player_2:discord.Member=None, player_3:discord.Member=None, player_4:discord.Member=None):

		role = ctx.guild.get_role(910400243596664843)
		if (role in ctx.author.roles):
			global winRequestPlayerID
			if(winRequestPlayerID != None):
				await ctx.reply("```❗ [ON GOING PROCESS]```")
			else:
				if(game_mode.lower() in ['s', 'd', 't', 'tournament']):
					winRequestPlayerID = ctx.author.id
					await arrange_winners(self, ctx, game_mode, player_1, player_2, player_3, player_4)
				else:
					await ctx.reply("Please select a valid gamemode s/d/t/tournamant")
		else:
			await ctx.reply("The role Win Manager is needed to add roles!")

	@commands.command()
	async def profile(self, ctx, player:discord.Member=None):
		if(player == None):
			player = ctx.author

		info = await fb.load_user_profile(player.id)
		total_wins = info['s'] + info['d'] + info['t'] + info['tournament']

		player_rank, rank_id, emoji = check_rank(total_wins)

		profile_embed=discord.Embed(title="{}  {}".format(emoji ,player_rank),color=0xe100ff)
		profile_embed.set_author(name="{}'s profile".format(player.name), icon_url=player.avatar_url)
		profile_embed.add_field(name="Solo Wins",value=info['s'], inline=True)
		profile_embed.add_field(name="Duo Wins",value=info['d'], inline=True)
		profile_embed.add_field(name="Trio Wins",value=info['t'], inline=True)
		profile_embed.add_field(name="Tournament Wins",value=info['tournament'], inline=True)
		profile_embed.set_footer(text="Total Wins: {}".format(total_wins))

		await ctx.reply(embed=profile_embed)

		await cache_data(player.id, info)		

async def arrange_winners(self, ctx, game_mode, player_1, player_2, player_3, player_4):
	#handle time
	temp_time = ctx.message.created_at
	datetime_new = temp_time + timedelta(hours = 4)
	date_new = str(datetime_new.date()).replace('-','/')
	time_new = str(datetime_new.time()).split('.')
	#handle users
	list_winners = [player_1,player_2,player_3,player_4]
	list_id=[]

	for player in list_winners:
		if(player != None):
			list_id.append(player.id)

	#handle gamemode
	list_gamemode = ['SOLO', 'DUO', 'TRIO', 'TOURNAMENT']
	game_mode_display = list_gamemode[['s', 'd', 't', 'tournament'].index(game_mode)]


	win_ticket=discord.Embed(title="{} | {} | {} | {}".format(db["scrim_index"],game_mode_display.upper(), date_new, time_new[0],color=0xe100ff))

	count = 0
	win_count = [[],[],[],[]]
	win_totals = [0, 0, 0, 0]

	for i in list_winners:
		if(i != None):
			win_count[count] = await fb.load_user_profile(list_id[count])
			win_count[count][game_mode] += 1
			win_ticket.add_field(name=i,value="{} : {}".format(game_mode_display.lower() ,win_count[count][game_mode]), inline=True)
			win_totals[count] = win_count[count]["s"] + win_count[count]["d"] + win_count[count]["t"] + win_count[count]['tournament']

		count += 1


	winner_ticket_ref = await ctx.reply(embed=win_ticket)
	prompt_ref = await ctx.reply("type `yes` to confirm details, `no` to abort the process")

	seconds = 0

	global winRequestPlayerID
	global response

	while seconds < 15:
		await asyncio.sleep(1)
		seconds += 1

		if(response != None):
			if(response == True):
				#add wins
				confirmation_msg = await ctx.reply("Writing to database")

				count = 0
				for id in list_id:
					if(id != "none"):
						await fb.update_user_profile(id, win_count[count])
						if(win_totals[count] > 0):
							name, id, emoji = check_rank(win_totals[count])
							if(id != None):
								guild = self.client.get_guild(803192609430044693)
								role = guild.get_role(id)
								await list_winners[count].add_roles(role)
						count += 1

				await confirmation_msg.edit(content="All details saved")

				global winner_tag_ch_id
				winner_tag = self.client.get_channel(winner_tag_ch_id)
				await winner_tag.send(embed=win_ticket)

				db["scrim_index"] = db["scrim_index"] + 1
				seconds = 100
			else:
				await ctx.reply("Aborting process")	
			
			seconds = 100
	
	if(response == None):
		await ctx.reply("No response. Aborting process")

	winRequestPlayerID = None
	response = None
	await winner_ticket_ref.delete()
	await prompt_ref.delete()

async def remove_win(self, ctx, amount, game_mode, player_1):
	wincount = await fb.load_user_profile(player_1.id)

	list_gamemode = ['SOLO', 'DUO', 'TRIO', 'TOURNAMENT']
	game_mode_display = list_gamemode[['s', 'd', 't', 'tournament'].index(game_mode)]

	await ctx.reply("Removing `{} {}` win(s) from {}. [from `{}` to `{}`]".format(amount,game_mode_display, player_1.mention, wincount[game_mode], wincount[game_mode] - amount))

	global winRequestPlayerID
	global response

	seconds = 0

	while seconds < 15:
		await asyncio.sleep(1)
		seconds += 1

		if(response != None):
			if(response == True):
				#add wins
				confirmation_msg = await ctx.reply("Writing to database")
				wincount[game_mode] -= amount
				if(wincount[game_mode] < 0):
					wincount[game_mode] = 0
				await fb.update_user_profile(player_1.id, wincount)
				await confirmation_msg.edit(content="All details saved")

				seconds = 100
			else:
				await ctx.reply("Aborting process")	
			
			seconds = 100
	
	if(response == None):
		await ctx.reply("No response. Aborting process")

	winRequestPlayerID = None
	response = None

def check_rank(wins:int):
	id = 0

	if(wins >= 1 and wins < 5):
		id = 1
	if(wins >= 5 and wins < 15):
		id = 2
	if(wins >= 15 and wins < 25):
		id = 3
	if(wins >= 25 and wins < 35):
		id = 4
	if(wins >= 35 and wins < 50):
		id = 5
	if(wins >= 50):
		id = 6
	if(wins < 0):
		id = 7
	
	ranks = ["Unranked", "Bronze", "Silver", "Gold", "Diamond", "Emerald", "Pink Star", "Best Player!"]
	ranks_id = [None, 806737098098737182, 806548115183370241, 806737694759321602, 806915515683045376, 806916098854879262, 809282944077135913, None]
	ranks_emote_id = ["<:unranked:854645341461807134>","<:Bronze:854663144474804244>" ,"<:Silver:854663144319090689>" , "<:Gold:854663144428797954>", "<:Diamond:854663144373485598>", "<:Emerald:854663144395243520>", "<:PinkStar:854663144538374164>", "<a:animatedfire:827187026163531857>" ]

	return ranks[id],ranks_id[id],ranks_emote_id[id]

async def arrange_leaderboard(self, ctx, gamemode):
	global leaderboard_cooldown

	if(leaderboard_cooldown == True):
		await ctx.reply('You are being rate limited. Please try again later')
		return

	leaderboard_cooldown = True
	msg = await ctx.reply("Arranging leaderboard")
	await fb.load_leaderboard(self, ctx, gamemode)
	await msg.delete()

	await asyncio.sleep(15)
	leaderboard_cooldown = False

async def arrange_leaderboard_admin(self, ctx, gamemode):
	msg = await ctx.reply("Arranging leaderboard")
	await fb.load_leaderboard(self, ctx, gamemode)
	await msg.delete()

async def cache_data(id, data):
	id = str(id)

	solo = {id:data['s']}
	duo = {id:data['d']}
	trio = {id:data['t']}
	tournament = {id:data['tournament']}

	await fb.cache_data('s', solo)
	await fb.cache_data('d', duo)
	await fb.cache_data('t', trio)
	await fb.cache_data('tournament', tournament)

def setup(client):
	client.add_cog(WinCounter(client))