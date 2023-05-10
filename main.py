import os
import discord
import mysql.connector
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the MySQL database
db = mysql.connector.connect(
    host="containers-us-west-35.railway.app:7522",  # Replace with your MySQL hostname
    user="root",  # Replace with your MySQL username
    password="DmSPXyiiiyKCpggPBJlC",  # Replace with your MySQL password
    database="railway"  # Replace with your MySQL database name
)
cursor = db.cursor()

# Create a table for invites if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Invites (
    GuildID BIGINT,
    Code VARCHAR(255),
    Uses INT,
    PRIMARY KEY (GuildID, Code)
)
""")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        for invite in await guild.invites():
            cursor.execute("INSERT INTO Invites VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Uses = %s", (guild.id, invite.code, invite.uses, invite.uses))
        db.commit()

@bot.event
async def on_member_join(member):
    # Get the welcome channel (replace with your channel's ID)
    welcome_channel = bot.get_channel(123456789012345678)
    info_channel1 = bot.get_channel(111111111111111111)  # Replace with your channel's ID
    info_channel2 = bot.get_channel(222222222222222222)  # Replace with your channel's ID

    for invite in await member.guild.invites():
        cursor.execute("SELECT Uses FROM Invites WHERE GuildID = %s AND Code = %s", (member.guild.id, invite.code))
        old_uses = cursor.fetchone()[0]
        if old_uses < invite.uses:
            await welcome_channel.send(f"{member.name} joined using invite code {invite.code}")
            cursor.execute("UPDATE Invites SET Uses = %s WHERE GuildID = %s AND Code = %s", (invite.uses, member.guild.id, invite.code))
            db.commit()

    role = discord.utils.get(member.guild.roles, id=1104611771060322327)  # Replace with your Role's ID
    await member.add_roles(role)

    # Send a welcome message and ping the new member
    await welcome_channel.send(f"Welcome {member.mention}! Please check out {info_channel1.mention} and {info_channel2.mention}.")

bot.run(os.getenv('BOT_TOKEN'))
