import sqlite3
import discord
import datetime
from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/moderation.sqlite")

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a user in this server")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        time = round(datetime.datetime.now().timestamp())
        database.execute("INSERT INTO Warns VALUES (?, ?, ?, ?)", (user.id, interaction.user.id, reason, time,)).connection.commit()
        embed = discord.Embed(
            title="You've been Warned!",
            description="**__Warning Information:__**\n"
                        f"**Moderator:** {interaction.user.mention}\n"
                        f"**Reason:** {reason}",
            color=discord.Color.red()
        )

        await user.send(embed=embed)
        await interaction.response.send_message(embed=discord.Embed(description=f"✅ Success! **{user.name}** has been warned.", color=discord.Color.green()), ephemeral=True)
    
    # @app_commands.command(name="unwarn", description="Remove a warning from a user")
    # async def unwarn(self, interaction: discord.Interaction, user: discord.Member, amount: int, reason: str=None):
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))