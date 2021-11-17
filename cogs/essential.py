import discord
from discord.ext import commands

item_shop_ch_id = 803200265926606889

class Essential(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Essential Module Ready")

	@commands.Cog.listener()
	async def on_message(self, message):
		if(message.author != self.client.user):
			if (message.channel.id == item_shop_ch_id):
				await send_code_promotion(message.channel)

		#await self.client.process_commands(message)


	#ping command

	@commands.command()
	async def ping(self, ctx):
		await ctx.send('Pong! {0} ms'.format(int(self.client.latency * 1000)))

	@commands.command()
	async def promote(self, ctx):
		if(ctx.author.id == 328229316301422592 or ctx.author.id == 607434055973077002):
			await send_code_promotion(ctx.channel)
		else:
			await ctx.send("You have to be sarwin or ishfaque to use this command :|")


async def send_code_promotion(channel):
	promote_msg=discord.Embed(title="__**SUPPORT THE SERVER**__", description="use code **Ish** in the _*Fortnite Item Shop*_ or in _Epic Games Luncher_ when purchasing cosmetic items or games.", color=0x00fbff)
	#promote_msg.set_footer(text="- ")
	await channel.send(embed=promote_msg)


def setup(client):
	client.add_cog(Essential(client))