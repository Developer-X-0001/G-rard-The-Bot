import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class GetPanelSelectorDelete(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GetPanelChoices())

class GetPanelChoices(Select):
    def __init__(self):
    
        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchall()
        choices = []
        for i in data:
            choices.append(discord.SelectOption(label=f'Panel - {i[0]}', description=f'Message ID: {i[1]}', value=i[0]))
        
        super().__init__(placeholder='Select a panel to delete!', min_values=1, max_values=1, options=choices, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT message_id, channel_id FROM ReactionRoles WHERE panel_id = ?", (self.values[0],)).fetchone()
        channel = interaction.guild.get_channel(data[1])
        try:
            message = channel.get_partial_message(data[0])
            await message.delete()
        except:
            pass
        database.execute("DELETE FROM ReactionRoles WHERE panel_id = ?", (self.values[0],)).connection.commit()
        database.execute(f"DROP TABLE '{self.values[0]}'").connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description=f"Success! `Panel - {self.values[0]}` has been deleted", color=discord.Color.red()), ephemeral=True)

        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchone()
        if data is not None:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=GetPanelSelectorDelete())
        else:
            embed = discord.Embed(
                description="There are no reaction roles panel available!",
                color=discord.Color.red()
            )

            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=None)
