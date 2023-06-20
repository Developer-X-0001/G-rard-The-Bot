import string
import config
import random
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Interface.EditItemView import ItemSelectorView

class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/shop.sqlite")

    shop_group = app_commands.Group(name="shop", description="Commands related to shoping system.")

    @shop_group.command(name="create-item", description="Create an item for the named price, availability and role.")
    @app_commands.choices(available=[
        app_commands.Choice(name="Yes", value='yes'),
        app_commands.Choice(name="No", value='no')
    ])
    async def create_item(self, interaction: discord.Interaction, name: str, price: int, available: app_commands.Choice[str], role: discord.Role):
        data = self.database.execute("SELECT name FROM Items WHERE name = ?", (name,)).fetchone()
        if data is None:
            id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
            self.database.execute("INSERT INTO Items VALUES (?, ?, ?, ?, ?)", (id, name, price, available.value, role.id,)).connection.commit()
            await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully created a new item: **`{}`**".format(name), color=discord.Color.green()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Item with name **`{}`** already exists!".format(name), color=discord.Color.red()), ephemeral=True)

    @shop_group.command(name="edit-items", description="Edit previously made items.")
    async def edit_item(self, interaction: discord.Interaction):
        data = self.database.execute("SELECT * FROM Items").fetchone()
        if data is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ There aren't any items available to edit!", color=discord.Color.red()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Please select an item to edit it's information.", color=discord.Color.blue()), view=ItemSelectorView(), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))