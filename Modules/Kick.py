import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/data.sqlite")

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str=None):
        if reason is None:
            reason = "No reason specified"
        
        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ You can't kick yourself!", color=discord.Color.red()), ephemeral=True)
            return

        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(embed=discord.Embed(description=f"✅ Success! **{user.name}** has been kicked from the server.", color=discord.Color.green()), ephemeral=True)
        except:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Oops! Something went wrong!", color=discord.Color.red()), ephemeral=True)
    
    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ `MissingPermissions`, You are missing (Kick Members) permission to use this command!", color=discord.Color.red()), ephemeral=True)
        if isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ `BotMissingPermissions`, I'm missing (Kick Members) permission!", color=discord.Color.red()), ephemeral=True)
        else:
            raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))