import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=1104611771060322327)  # Replace with your Role's ID
    await member.add_roles(role)

bot.run(os.getenv('BOT_TOKEN'))
