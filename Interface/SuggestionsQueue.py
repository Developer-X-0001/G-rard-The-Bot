import sqlite3
import discord
import datetime
from discord import ButtonStyle
from discord.ui import View, Select, button, Button
from Interface.SuggestionButtons import SuggestionButtonsView

database = sqlite3.connect("./Databases/suggestions.sqlite")

class SuggestionsQueueView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SuggestionSelector())

class SuggestionSelector(Select):
    def __init__(self):
        queue_data = database.execute("SELECT suggestion_id, user_id, suggestion FROM Queue").fetchall()
        options = []

        for suggestion in queue_data:
            options.append(discord.SelectOption(label=f"{suggestion[0]} - {suggestion[2]}", description=f"Submitter ID: {suggestion[1]}", value=suggestion[0]))

        super().__init__(placeholder='Select a Suggestion', min_values=1, max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT user_id, suggestion FROM Queue WHERE suggestion_id = ?", (self.values[0],)).fetchone()
        user = interaction.guild.get_member(data[0])
        embed = discord.Embed(timestamp=datetime.datetime.now(), color=discord.Color.dark_blue())
        embed.add_field(name="Submitter", value=user.mention, inline=False)
        embed.add_field(name="Suggestion", value=data[1], inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Submitter ID: {user.id}")
        await interaction.response.edit_message(embed=embed, view=SuggestionButtons(self.values[0]))

class SuggestionButtons(View):
    def __init__(self, suggestion_id: str):
        self.suggestion_id = suggestion_id
        super().__init__(timeout=None)

    @button(label="Approve", style=ButtonStyle.green, row=1)
    async def approve(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT suggestions_channel_id FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        suggestion_data = database.execute("SELECT suggestion_id, user_id, suggestion FROM Queue WHERE suggestion_id = ?", (self.suggestion_id,)).fetchone()
        thread_data = database.execute("SELECT thread_status FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        channel = interaction.guild.get_channel(data[0])
        user = interaction.guild.get_member(suggestion_data[1])

        embed = discord.Embed(
            timestamp=datetime.datetime.now(),
            color=discord.Color.gold()
        )
        embed.add_field(name="Submitter", value=user.mention, inline=False)
        embed.add_field(name="Suggestion", value=suggestion_data[2], inline=False)
        embed.add_field(name="Results so far", value="⏫ **0**\n⏬ **0**")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"User ID: {user.id} | sID: {suggestion_data[0]}")

        msg = await channel.send(embed=embed, view=SuggestionButtonsView())
        if thread_data is not None and thread_data[0] == 'Enabled':
            await msg.create_thread(name=f"Thread for suggestion {suggestion_data}")
        database.execute("DELETE FROM Queue WHERE suggestion_id = ?", (self.suggestion_id,)).connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description=f"✅ `Suggestion - {suggestion_data[0]}` has been approved!", color=discord.Color.green()), ephemeral=True)
        database.execute("INSERT INTO Suggestions VALUES (?, ?, ?, ?, NULL)", (msg.id, self.suggestion_id, user.id, suggestion_data[2],)).connection.commit()
        database.execute(f"CREATE TABLE IF NOT EXISTS '{self.suggestion_id}' (upvotes INTERGER, downvotes INTEGER)")
        queue_data = database.execute("SELECT suggestion_id, user_id, suggestion FROM Queue").fetchall()
        if queue_data == []:
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(description="⚠ No suggestions available in queue", color=discord.Color.gold()), view=None)
            return
        else:
            embed = discord.Embed(
                title="Suggestions Queue",
                description="There are `{}` suggestions available in queue. Select a suggestion from the dropdown below to approve or decline it.".format(len(queue_data)),
                color=discord.Color.blue()
            )

            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=SuggestionsQueueView())

    
    @button(label="Decline", style=ButtonStyle.red, row=1)
    async def decline(self, interaction: discord.Interaction, button: Button):
        database.execute("DELETE FROM Queue WHERE suggestion_id = ?", (self.suggestion_id,)).connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description=f"🗑️ `Suggestion - {self.suggestion_id}` has been removed.", color=discord.Color.light_gray()), ephemeral=True)