import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, Button, button

database = sqlite3.connect("./Databases/shop.sqlite")
user_database = sqlite3.connect("./Databases/activity.sqlite")

class RedeemButton(View):
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(timeout=None)

    @button(label="Redeem", style=ButtonStyle.blurple)
    async def redeem_button(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT role FROM Items WHERE id = ?", (self.item_id,)).fetchone()
        role = interaction.guild.get_role(data[0])

        if role in interaction.user.roles:
            redeem_settings = database.execute("SELECT redeem_channel, redeem_role FROM RedeemSettings WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
            redeem_manager_role = interaction.guild.get_role(redeem_settings[1])
            redeem_logs_channel = interaction.guild.get_channel(redeem_settings[0])

            redeem_embed = discord.Embed(
                title=""
            )