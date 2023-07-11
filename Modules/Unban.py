import config
import string
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")

    @app_commands.command(name="unban", description="Unbans a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def _unban(self, interaction: discord.Interaction, user_id: str, reason: str=None):
        if user_id.isdigit():
            user = await self.bot.fetch_user(user_id)

            if user == interaction.user:
                await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't ban yourself!**", color=discord.Color.red()), ephemeral=True)
                return
            
            if reason is None:
                reason = "Not specified"
            
            bans = [entry.user async for entry in interaction.guild.bans()]

            if user in bans:
                id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                await interaction.guild.unban(user=user, reason=reason)
                self.database.execute("DELETE FROM Bans WHERE user_id = ?", (user_id,)).connection.commit()
                await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been successfully unbanned from the server.".format(user.name), color=discord.Color.green()), ephemeral=True)
                self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, interaction.user.id, 'unban', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
            
            else:
                await interaction.response.send_message(embed=discord.Embed(description="❌ **{}** isn't banned from the server!".format(user.name), color=discord.Color.red()), ephemeral=True)
        
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Please put a valid user id!", color=discord.Color.red()), ephemeral=True)
        
    @_unban.error
    async def unban_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ You are missing (Ban Members) permission to run this command!", color=discord.Color.red()), ephemeral=True)
            return
        else:
            raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))