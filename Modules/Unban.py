import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/moderation.sqlite")

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Unbans a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def _unban(self, interaction: discord.Interaction, user_id: int, reason: str=None):
        user = self.bot.get_user(id=user_id)

        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't ban yourself!**", color=discord.Color.red()), ephemeral=True)
            return
        
        if reason is None:
            reason = "Not specified"
        
        bans = [user async for user in interaction.guild.bans()]

        if user in bans:
            await interaction.guild.unban(user=user, reason=reason)
            database.execute("DELETE FROM Bans WHERE user_id = ?", (user_id,)).connection.commit()
            await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been successfully unbanned from the server.".format(user.name), color=discord.Color.green()), ephemeral=True)
        
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **{}** isn't banned from the server!".format(user.name), color=discord.Color.red()), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))