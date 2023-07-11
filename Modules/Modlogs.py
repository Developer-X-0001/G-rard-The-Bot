import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Modlogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")

    @app_commands.command(name="modlogs", description="Check moderation history of a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def modlogs(self, interaction: discord.Interaction, user: discord.Member):
        data = self.database.execute("SELECT mod_id, action, action_at FROM Modlogs WHERE user_id = ? ORDER BY action_at DESC", (user.id,)).fetchall()
        if data:
            user_data = ""
            counter = 1

            for entry in data:
                moderator = interaction.guild.get_member(entry[0])
                new_entry = f"{counter}. {entry[1].capitalize()} | <t:{entry[2]}:d> | By: {moderator.mention}\n"
                if (len(user_data) + len(new_entry)) > 4096:
                    break
                user_data += new_entry
                counter += 1

            modlogs_embed = discord.Embed(
                title=f"{user.global_name}'s Moderation History",
                description=user_data,
                color=discord.Color.blue()
            )
            modlogs_embed.set_footer(text="Showing most recent 30 infractions.")

            await interaction.response.send_message(embed=modlogs_embed, ephemeral=True)
        
        else:
            modlogs_embed = discord.Embed(
                title=f"{user.global_name}'s Moderation History",
                description="No infractions found...",
                color=discord.Color.blue()
            )

            await interaction.response.send_message(embed=modlogs_embed, ephemeral=True)
        
    @modlogs.error
    async def modlogs_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(description="❌ You are missing (Administrator) permission to run this command!", color=discord.Color.red()), ephemeral=True)
            return
        else:
            raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(Modlogs(bot))