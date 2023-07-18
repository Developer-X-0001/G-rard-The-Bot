import re
import string
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")

    @app_commands.command(name="warn", description="Warn a user in this server")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, duration: str=None):
        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't warn yourself!**", color=discord.Color.red()), ephemeral=True)
            return
        
        if reason is None:
            reason = "Not specified"

        if duration is None:
            warn_type = 'permanent'
            warn_embed = discord.Embed(
                title="Warning Logged",
                description=f"**{user.name}** has been warned.\n\n**Moderator:** {interaction.user.mention}\n**Reason:** {reason}\n**Warn Duration:** Permanent",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=warn_embed)

            warned_at = round(datetime.datetime.now().timestamp())
            id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()

            self.database.execute(
                "INSERT INTO Warns VALUES (?, ?, NULL, ?, ?, ?)",
                (
                    user.id,
                    warned_at,
                    interaction.user.id,
                    warn_type,
                    reason,
                )
            ).connection.commit()
            self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, interaction.user.id, 'warn', warned_at, reason,)).connection.commit()

            data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT warn_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
            if data is None:
                return
            
            else:
                channel = interaction.guild.get_channel(data[0])
                await channel.send(embed=discord.Embed(title="Warning Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}\n**Duration:** Permanent", color=discord.Color.blue()))
                return
    
        if duration:
            pattern = r'(\d+s)?(\d+m)?(\d+h)?(\d+d)?'
            match = re.match(pattern, duration)

            if match:
                warn_type = 'temporary'
                seconds = int(match.group(1)[:-1]) if match.group(1) else 0
                minutes = int(match.group(2)[:-1]) if match.group(2) else 0
                hours = int(match.group(3)[:-1]) if match.group(3) else 0
                days = int(match.group(4)[:-1]) if match.group(4) else 0

                total_seconds = seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60 * 60)

                expiry = round(datetime.datetime.now().timestamp()) + total_seconds

                warn_embed = discord.Embed(
                    title="Warning Logged",
                    description=f"**{user.name}** has been warned.\n\n**Moderator:** {interaction.user.mention}\n**Reason:** {reason}\n**Warn Duration:** {duration}",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=warn_embed, ephemeral=True)

                warned_at = round(datetime.datetime.now().timestamp())
                id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()

                self.database.execute(
                    "INSERT INTO Warns VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user.id,
                        warned_at,
                        expiry,
                        interaction.user.id,
                        warn_type,
                        reason,
                    )
                ).connection.commit()
                self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, interaction.user.id, 'warn', warned_at, reason,)).connection.commit()

                data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT warn_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
                if data is None:
                    return
                
                else:
                    channel = interaction.guild.get_channel(data[0])
                    await channel.send(embed=discord.Embed(title="Warning Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}\n**Duration:** {duration}", color=discord.Color.blue()))
                    return
            
            else:
                error_embed = discord.Embed(
                    title="Invalid time specification!",
                    description="**You have entered an invalid time!**\nUse a valid time code. Time codes can consist of several times ending with s (second), m (minute), h (hour), d (day) or w (week).\nExamples: 15m for 15 minutes, 1h for 1 hour, 3d for 3 days, 3d5h2m for 3 days, 5 hours and 2 minutes\n\nPS: You can click on the blue `/warn` command above this message to receive a copy of the used command for your warn",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))