import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Interface.RedeemView import RedeemButton

class Redeem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/shop.sqlite")

    @app_commands.command(name="redeem", description="Redeem a listed item.")
    async def _redeem(self, interaction: discord.Interaction, item: str):
        data = self.database.execute("SELECT name, price, available, role FROM Items WHERE id = ?", (item,)).fetchone()
        
        role = interaction.guild.get_role(data[3])

        item_embed = discord.Embed(
            title="Editing Item",
            color=discord.Color.blue()
        )
        item_embed.add_field(name="Name:", value=data[0], inline=False)
        item_embed.add_field(name="Price:", value=data[1], inline=False)
        item_embed.add_field(name="Availability:", value="Available" if data[2] == 'yes' else 'Not Available', inline=False)
        item_embed.add_field(name="Role:", value=role.mention, inline=False)
        item_embed.set_footer(text="You must have the required role to redeem this item!")

        await interaction.response.send_message(embed=item_embed, view=RedeemButton(item_id=item), ephemeral=True)
    
    @_redeem.autocomplete('item')
    async def redeem_autocomplete_callback(self, interaction: discord.Interaction, current: str):
        data = self.database.execute("SELECT id, name, price FROM Items").fetchall()

        return [
            app_commands.Choice(name=f"{item[1]} - {item[2]} Points", value=item[0]) for item in data
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(Redeem(bot))