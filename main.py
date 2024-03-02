import os
import discord
import psutil
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

server_stats_message_id = None

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    send_server_stats.start()

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=1104611771060322327)  # Replace with your Role's ID
    await member.add_roles(role)

@tasks.loop(minutes=15)
async def send_server_stats():
    global server_stats_message_id
    channel = bot.get_channel(1104614020352315464)  # Your specified channel ID

    # Gather server stats
    mem = psutil.virtual_memory()
    total_ram_mb = mem.total / (1024 * 1024)
    used_ram_mb = mem.used / (1024 * 1024)
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    net_io = psutil.net_io_counters()
    uptime = os.popen('uptime -p').readline().strip()
    tasks_count = len(psutil.pids())
    system = os.popen('uname -a').readline().strip()

    # Modify the embed with the server stats
    embed = discord.Embed(title="Server Stats", color=0x00ff00)
    embed.add_field(name="Total RAM", value=f"{total_ram_mb:.2f} MB", inline=True)
    embed.add_field(name="Used RAM", value=f"{used_ram_mb:.2f} MB", inline=True)
    embed.add_field(name="CPU Usage", value=f"CPU 0: {cpu[0]}%, CPU 1: {cpu[1]}%", inline=True)
    embed.add_field(name="Network I/O", value=f"Sent {net_io.bytes_sent} bytes, Received {net_io.bytes_recv} bytes", inline=False)
    embed.add_field(name="Uptime", value=uptime, inline=False)
    embed.add_field(name="Total Running Tasks", value=tasks_count, inline=True)
    embed.add_field(name="System Info", value=system, inline=False)

    # Send or edit the embed message
    if server_stats_message_id is None:
        message = await channel.send(embed=embed)
        server_stats_message_id = message.id
    else:
        try:
            message = await channel.fetch_message(server_stats_message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            server_stats_message_id = message.id

bot.run(os.getenv('BOT_TOKEN'))
