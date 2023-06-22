import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands

class Redeem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/shop.sqlite")

    @app_commands.command(name="redeem", description="Redeem a listed item.")
    async def _redeem(self, interaction: discord.Interaction, item: str):
        print()
    
    @_redeem.autocomplete('item')
    async def redeem_autocomplete_callback(self, interaction: discord.Interaction, current: str):
        data = self.database.execute("SELECT id, name, price FROM Items").fetchall()

        return [
            app_commands.Choice(name=f"{item[1]} - {item[2]} Points", value=item[0]) for item in data
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(Redeem(bot))