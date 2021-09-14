import discord
from discord.ext import commands
import asyncio

class Registration(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Registration Module Ready")

	#send the message (click to register in the channel)
	@commands.command()
	async def set_registration_channel(self, ctx):
		await ctx.message.delete()

		if(ctx.author.id == 328229316301422592):
			await send_registration_message(ctx.channel)
		else:
			error_msg = await ctx.send("You have to be sarwin to use this command :]")
			await asyncio.sleep(5)
			await error_msg.delete()


async def send_registration_message(channel):
	register_embed=discord.Embed(title="__**Epic Account Registration**__", description="Please click on the raised hand below to link your Epic Account. You will receive a direct message from Scrim Manager with further instructions. Make sure your DM is enable and open. If there are any issue, contact any Staff Member", color=0x00fbff)
	register_embed.set_footer(text="Made with ❤ by sarwin")
	register_msg = await channel.send(embed=register_embed)

	await register_msg.add_reaction("✋")


def setup(client):
	client.add_cog(Registration(client))