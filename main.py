import os
import discord
from discord.ext import commands
from keep_alive import keep_alive
import database_access as db

discord_token = os.environ['TOKEN']

client = commands.Bot(command_prefix = ".")

@client.event
async def on_ready():
	db.initialize_database()
	print("Bot ready")

@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send("{} module was enable".format(extension))

@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	await ctx.send("{} module was disable".format(extension))

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

keep_alive()
client.run(discord_token)