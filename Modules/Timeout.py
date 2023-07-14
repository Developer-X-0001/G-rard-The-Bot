import string
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Timeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")
    
    @app_commands.command(name="timeout", description="Timeout a user.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.choices(duration=[
        app_commands.Choice(name="60 secs", value=60),
        app_commands.Choice(name="5 mins", value=300),
        app_commands.Choice(name="10 mins", value=600),
        app_commands.Choice(name="1 hour", value=3600),
        app_commands.Choice(name="1 day", value=86400),
        app_commands.Choice(name="1 week", value=604800)
    ])
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Choice[int], reason: str=None):
        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't timeout yourself!**", color=discord.Color.red()), ephemeral=True)
            return
        
        if reason is None:
            reason = "Not specified"
        
        await user.timeout(datetime.timedelta(seconds=duration.value), reason=reason)
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
        self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, interaction.user.id, 'timeout', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been timed-out for {}.\n**Expires In:** <t:{}:R>".format(user.name, duration.name, (round(datetime.datetime.now().timestamp() + duration.value)),), color=discord.Color.green()), ephemeral=True)

        data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT timeout_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data is None:
            return
        else:
            channel = interaction.guild.get_channel(data[0])
            await channel.send(embed=discord.Embed(title="Mute/Timeout Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}\n**Duration:** {duration.name}", color=discord.Color.blue()))
            return

    @timeout.error
    async def timeout_error(self, interaction: discord.Interaction, error: app_commands.errors.AppCommandError):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ You are missing (Timeout Members) permission to run this command!", color=discord.Color.red()), ephemeral=True)
            return
        else:
            raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(Timeout(bot))