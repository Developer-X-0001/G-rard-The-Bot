import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import Select, View, Button, button, select

database = sqlite3.connect("./Databases/polls.sqlite")

class PollSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)

class PollSelector(Select):
    def __init__(self):
        normal_polls_data = database.execute("SELECT poll_id, question, status FROM NormalPolls").fetchall()
        timed_polls_data = database.execute("SELECT poll_id, question, status FROM TimedPolls").fetchall()

        data = normal_polls_data + timed_polls_data
        choices = []
        for entry in data:
            choices.append(discord.SelectOption(label="ID: {}".format(entry[0]), emoji='🟢' if entry[2] == 'open' else '🔴', description=entry[1], value=entry[0]))

    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT poll_id, status, user_id, question, choices, result, maxchoices, allowedrole, channel_id, created_at, closed_at FROM ")
        
        
        poll_embed = discord.Embed()

class PollInformationView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Go Back", style=ButtonStyle.gray)
    async def go_back_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            description="Select a poll from the dropdown menu to view it's information.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=PollSelectorView())