import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, Button, button

database = sqlite3.connect("./Databases/shop.sqlite")
user_database = sqlite3.connect("./Databases/activity.sqlite")

class RedeemRequestView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Mark as Delivered", style=ButtonStyle.green, custom_id="mark_as_delivered")
    async def mark_as_delivered_button(self, interaction: discord.Interaction, button: Button):
        item_id = interaction.message.embeds[0].fields[0].value
        print()

    @button(label="Reject Request", style=ButtonStyle.red, custom_id="reject_request")
    async def reject_request_button(self, interaction: discord.Interaction, button: Button):
        print()

    @button(label="Close Thread", style=ButtonStyle.gray, custom_id="close_thread", row=1)
    async def close_thread_button(self, interaction: discord.Interaction, button: Button):
        print()