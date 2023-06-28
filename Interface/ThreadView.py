import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, Button, button

database = sqlite3.connect("./Databases/shop.sqlite")

class ThreadView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Close Thread", style=ButtonStyle.red, custom_id="close_thread")
    async def close_thread_button(self, interaction: discord.Interaction, button: Button):
        thread = interaction.guild.get_thread(interaction.message.channel.id)
        await thread.edit(invitable=False)
        self.close_thread_button.disabled = True
        self.re_open_thread_button.disabled = True
        self.re_open_thread_button.style = ButtonStyle.gray
        await interaction.response.edit_message(view=self)
    
    @button(label="Re-Open Thread", style=ButtonStyle.green, custom_id="re_open_thread")
    async def re_open_thread_button(self, interaction: discord.Interaction, button: Button):
        thread = interaction.guild.get_thread(interaction.message.channel.id)
        await thread.edit(locked=False)
        self.close_thread_button.disabled = True
        self.close_thread_button.style = ButtonStyle.gray
        self.re_open_thread_button.disabled = True
        await interaction.response.edit_message(view=self)