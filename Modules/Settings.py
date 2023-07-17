import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Interface.SettingsView import SettingsView

database = sqlite3.connect("./Databases/settings.sqlite")

class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="settings", description="Configure the bot in the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(self, interaction: discord.Interaction):
        settings_embed = discord.Embed(
            title=f"{interaction.guild.name} Settings",
            color=discord.Color.blue()
        )
        if interaction.guild.icon:
            settings_embed.set_thumbnail(url=interaction.guild.icon.url)
        
        data = database.execute("SELECT warn_log_channel, ban_log_channel, kick_log_channel, timeout_log_channel, role_log_channel FROM LogChannels WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data:
            settings_embed.add_field(
                name="Logging Channels:",
                value=f'''Ban Logs - {'Not set' if data[1] is None else interaction.guild.get_channel(data[1]).mention}
                        Kick Logs - {'Not set' if data[2] is None else interaction.guild.get_channel(data[2]).mention}
                        Timeout Logs - {'Not set' if data[3] is None else interaction.guild.get_channel(data[3]).mention}
                        Warning Logs - {'Not set' if data[0] is None else interaction.guild.get_channel(data[0]).mention}
                        Role Update Logs - {'Not set' if data[4] is None else interaction.guild.get_channel(data[4]).mention}
                    ''',
                inline=False
            )
        
        else:
            settings_embed.add_field(
                name="Logging Channels:",
                value=f'''Ban Logs - Not set
                        Kick Logs - Not set
                        Timeout Logs - Not set
                        Warning Logs - Not set
                        Role Update Logs - Not set
                    ''',
                inline=False
            )

        await interaction.response.send_message(embed=settings_embed, view=SettingsView(), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))