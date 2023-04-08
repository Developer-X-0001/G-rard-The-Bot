import json
import sqlite3
import discord
from discord import ButtonStyle
from discord.ui import View, Select, Button, button
from Interface.SelectMenus import ChannelSelector, RoleSelector

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class SendReactionRole(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)

    @button(label="Send to Channel", style=ButtonStyle.green, custom_id="send_to_channel")
    async def sendToChannel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=ChannelSelector(self.panel_id))
    
    @button(label="Send Here", style=ButtonStyle.green, custom_id="send_here")
    async def sendHere(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        msg = await channel.send(embed=interaction.message.embeds[0], view=RoleSelector(self.panel_id))
        database.execute("UPDATE ReactionRoles SET message_id = ?, channel_id = ? WHERE panel_id = ?", (msg.id, channel.id, self.panel_id,)).connection.commit()
        await interaction.response.edit_message(embed=discord.Embed(description=f"✅ Success! A new reaction roles panel has been generated in {channel.mention}"), view=None)

class GetPanelSelectorSend(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GetPanelChoices())

class GetPanelChoices(Select):
    def __init__(self):
    
        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchall()
        choices = []
        for i in data:
            choices.append(discord.SelectOption(label=f'Panel - {i[0]}', description=f'Message ID: {i[1]}', value=i[0]))
        
        super().__init__(placeholder='Select a panel to edit!', min_values=1, max_values=1, options=choices, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT message_id, channel_id, embed FROM ReactionRoles WHERE panel_id = ?", (self.values[0],)).fetchone()
        embed_str = json.loads(data[2])
        get_embed = discord.Embed.from_dict(embed_str)

        try:
            channel = interaction.guild.get_channel(data[1])
            message = await channel.fetch_message(data[0])
            await message.delete()
            await interaction.response.edit_message(embed=message.embeds[0], view=SendReactionRole(self.values[0]))
        except:

            await interaction.response.edit_message(embed=get_embed, view=SendReactionRole(self.values[0]))
