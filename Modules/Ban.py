import re
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")

    @app_commands.command(name="ban", description="Ban a member from the server for a specified duration.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.choices(delete_messages=[
        app_commands.Choice(name="Don't Delete Any", value=0),
        app_commands.Choice(name="Previous Hour", value=3600),
        app_commands.Choice(name="Previous 6 Hours", value=21600),
        app_commands.Choice(name="Previous 12 Hours", value=43200),
        app_commands.Choice(name="Previous 24 Hours", value=86400),
        app_commands.Choice(name="Previous 3 Days", value=259200),
        app_commands.Choice(name="Previous 7 Days", value=604800)
    ])
    @app_commands.describe(
        user="User whom you are banning.",
        delete_messages="How much of their recent message history to delete?",
        duration="How long the ban should last? Leave none for permanent ban.",
        reason="Reason for ban"
    )
    async def _ban(self, interaction: discord.Interaction, user: discord.Member, delete_messages: app_commands.Choice[int], duration: str=None, reason: str=None):
        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't ban yourself!**", color=discord.Color.red()), ephemeral=True)
            return
        
        if reason is None:
            reason = "Not specified"

        data = self.database.execute("SELECT user_id FROM Bans WHERE user_id = ?", (user.id,)).fetchone()

        if data:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **{}** is already banned from the server!".format(user.name), color=discord.Color.red()), ephemeral=True)
            return

        if duration is None:
            ban_type = 'permanent'
            self.database.execute(
                '''
                    INSERT INTO Bans VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                ''',
                (
                    user.id,
                    round(datetime.datetime.now().timestamp()),
                    None,
                    interaction.user.id,
                    ban_type,
                    reason,
                )
            ).connection.commit()
            await interaction.guild.ban(user=user, delete_message_seconds=delete_messages.value, reason=reason,)
            await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been banned from the server.\n**Ban Type:** {}\n**Ban Expiring in:** {}\n**Reason:** {}".format(user.name, ban_type.capitalize(), 'Never', reason), color=discord.Color.green()), ephemeral=True)
        
            data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT ban_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
            if data is None:
                return
            
            else:
                channel = interaction.guild.get_channel(data[0])
                await channel.send(embed=discord.Embed(title="Ban Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}\n**Duration:** Permanent", color=discord.Color.blue()))
                return

        if duration:
            ban_type = 'temporary'
            pattern = r'(\d+s)?(\d+m)?(\d+h)?(\d+d)?'
            match = re.match(pattern, duration)

            if match:
                seconds = int(match.group(1)[:-1]) if match.group(1) else 0
                minutes = int(match.group(2)[:-1]) if match.group(2) else 0
                hours = int(match.group(3)[:-1]) if match.group(3) else 0
                days = int(match.group(4)[:-1]) if match.group(4) else 0

                total_seconds = seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60 * 60)

                expiry = round(datetime.datetime.now().timestamp()) + total_seconds

                self.database.execute(
                    '''
                        INSERT INTO Bans VALUES (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?
                        )
                    ''',
                    (
                        user.id,
                        round(datetime.datetime.now().timestamp()),
                        expiry,
                        interaction.user.id,
                        ban_type,
                        reason,
                    )
                ).connection.commit()
                await interaction.guild.ban(user=user, delete_message_seconds=delete_messages.value, reason=reason,)
                await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been banned from the server.\n**Ban Type:** {}\n**Ban Expiring in:** <t:{}:f>\n**Reason:** {}".format(user.name, ban_type.capitalize(), expiry, reason), color=discord.Color.green()), ephemeral=True)

                data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT ban_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
                if data is None:
                    return
                
                else:
                    channel = interaction.guild.get_channel(data[0])
                    await channel.send(embed=discord.Embed(title="Ban Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}\n**Duration:** {duration}", color=discord.Color.blue()))
                    return
            
            else:
                error_embed = discord.Embed(
                    title="Invalid time specification!",
                    description="**You have entered an invalid time!**\nUse a valid time code. Time codes can consist of several times ending with s (second), m (minute), h (hour), d (day) or w (week).\nExamples: 15m for 15 minutes, 1h for 1 hour, 3d for 3 days, 3d5h2m for 3 days, 5 hours and 2 minutes\n\nPS: You can click on the blue `/ban` command above this message to receive a copy of the used command for your ban",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @_ban.error
    async def ban_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ You are missing (Ban Members) permission to run this command!", color=discord.Color.red()), ephemeral=True)
            return
        else:
            raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))