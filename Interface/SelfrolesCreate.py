import json
import config
import string
import random
import sqlite3
import discord
from discord.ext import commands
from Functions.ColorChecks import int_to_hex
from discord import app_commands, ButtonStyle, TextStyle
from Interface.SelectMenus import RoleSelector, ChannelSelector
from discord.ui import Button, button, View, Select, select, TextInput, Modal
from Interface.Modals import EditTitleModal, EditDescModal, EditColorModal, AddChoiceModal

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class EditChoiceModal(Modal, title="Edit An Existing Choice"):
    def __init__(self, panel_id, role_id):
        self.panel_id = panel_id
        self.role_id = role_id
        super().__init__(timeout=None)

        data = database.execute(f"SELECT name, emoji, description FROM '{panel_id}' WHERE role_id = ?", (role_id,)).fetchone()

        self.choice_name = TextInput(
            label='Name',
            style=TextStyle.short,
            placeholder='Enter choice name',
            default=data[0],
            required=True
        )
        self.choice_role = TextInput(
            label='Role ID',
            style=TextStyle.short,
            placeholder='Enter ID of the target Role',
            default=role_id,
            required=True
        )
        self.choice_emoji = TextInput(
            label='Emoji',
            style=TextStyle.short,
            placeholder='Enter UNICODE Emoji Only!! e.g 🌐, 🎉',
            default=data[1],
            required=False
        )
        self.choice_description = TextInput(
            label='Description',
            style=TextStyle.short,
            placeholder='Enter choice description',
            default=data[2],
            required=False
        )

        self.add_item(self.choice_name)
        self.add_item(self.choice_role)
        self.add_item(self.choice_emoji)
        self.add_item(self.choice_description)

    async def on_submit(self, interaction: discord.Interaction):
        database.execute(f"UPDATE '{self.panel_id}' SET name = ?, role_id = ?, emoji = ?, description = ? WHERE role_id = ?", (str(self.choice_name), str(self.choice_role), str(self.choice_emoji), str(self.choice_description), self.role_id,)).connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description="Success, Choice updated.", color=discord.Color.green()), ephemeral=True)

class EditChoiceSelector(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)
        self.add_item(GetChoices(panel_id))
    
    @button(label="Go Back", style=ButtonStyle.blurple, custom_id="go_back", row=1)
    async def goBack(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=ConfigureChoices(self.panel_id))

class GetChoices(Select):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
    
        data = database.execute(f"SELECT name, role_id, emoji, description FROM '{self.panel_id}'").fetchall()
        choices = []
        for i in data:
            choices.append(discord.SelectOption(label=i[0], emoji=i[2], description=f'Role ID: {i[1]}', value=i[1]))
        
        super().__init__(placeholder='Select a role choice to configure!', min_values=1, max_values=1, options=choices, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditChoiceModal(self.panel_id, int(self.values[0])))

class EditAllowedSelection(View):
    def __init__(self, panel_id: str, selection_amount: int):
        self.panel_id = panel_id
        super().__init__(timeout=None)
        self.add_item(SetAmountSelection(panel_id, selection_amount))

    @button(label="Go Back", style=ButtonStyle.blurple, custom_id="go_back", row=1)
    async def goBack(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=ConfigureChoices(self.panel_id))

class SetAmountSelection(Select):
    def __init__(self, panel_id: str, selection_amount: int):
        self.panel_id = panel_id

        choices = []
        for i in range(1, (selection_amount + 1)):
            choices.append(discord.SelectOption(label=i, value=i))
        
        super().__init__(placeholder="Choice allowed selections on this panel!", min_values=1, max_values=1, options=choices, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        database.execute(f"UPDATE ReactionRoles SET choices = {self.values[0]} WHERE panel_id = '{self.panel_id}'").connection.commit()
        await interaction.response.edit_message(view=ConfigureChoices(self.panel_id))

class ConfigureChoices(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)

    @button(label="Add Choice", style=ButtonStyle.green, custom_id="add_new_choice")
    async def addNewChoice(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(AddChoiceModal(ConfigureChoices(self.panel_id), self.panel_id))

    @button(label="Edit Choices", style=ButtonStyle.green, custom_id="edit_choices")
    async def editChoices(self, interaction: discord.Interaction, button: Button):
        data = database.execute(f"SELECT name, role_id, emoji, description FROM '{self.panel_id}'").fetchone()
        if data is not None:
            await interaction.response.edit_message(view=EditChoiceSelector(self.panel_id))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Error, There are no choices made for this panel.", color=discord.Color.red()), ephemeral=True)
    
    @button(label="Delete Choices", style=ButtonStyle.red, custom_id="delete_choices")
    async def deleteChoices(self, interaction: discord.Interaction, button: Button):
        data = database.execute(f"SELECT name, role_id, emoji, description FROM '{self.panel_id}'").fetchone()
        if data is not None:
            await interaction.response.edit_message(view=EditChoiceSelector(self.panel_id))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Error, There are no choices made for this panel.", color=discord.Color.red()), ephemeral=True)
    
    @button(label="Allowed Selections", style=ButtonStyle.blurple, custom_id="allowed_selections")
    async def allowedSelections(self, interaction: discord.Interaction, button: Button):
        data = database.execute(f"SELECT name, role_id, emoji, description FROM '{self.panel_id}'").fetchall()
        if data != []:
            await interaction.response.edit_message(view=EditAllowedSelection(self.panel_id, len(data)))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Error, There are no choices made for this panel.", color=discord.Color.red()), ephemeral=True)
    
    @button(label="Go Back", style=ButtonStyle.blurple, custom_id="go_back_2", row=1)
    async def goBack(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=CreateSelfRoles(self.panel_id))


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

class EmbedEditButtons(View):
    def __init__(self, panel_id):
        self.panel_id = panel_id
        super().__init__(timeout=None)

    @button(label="Edit Title", style=ButtonStyle.green, custom_id="edit_title")
    async def editTitle(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        await interaction.response.send_modal(EditTitleModal(embed.title if embed.title else None))
    
    @button(label="Edit Description", style=ButtonStyle.green, custom_id="edit_desc")
    async def editDesc(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        await interaction.response.send_modal(EditDescModal(embed.description if embed.description else None))
    
    @button(label="Edit Color", style=ButtonStyle.green, custom_id="edit_color")
    async def editColor(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        color = '#' + int_to_hex(embed.color.value)
        await interaction.response.send_modal(EditColorModal(color))
    
    @button(label="Go Back", style=ButtonStyle.blurple, custom_id="go_back")
    async def goBack(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=CreateSelfRoles(self.panel_id))

class CreateSelfRoles(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)

    @button(label="Save", style=ButtonStyle.blurple, custom_id="save")
    async def save(self, interaction: discord.Interaction, button: Button):
        data = database.execute(f"SELECT name, role_id, emoji, description FROM '{self.panel_id}'").fetchone()
        if data is not None:
            embed = interaction.message.embeds[0]
            embed_str = json.dumps(embed.to_dict())
            database.execute(f"UPDATE ReactionRoles SET embed = ? WHERE panel_id = '{self.panel_id}'", (embed_str,)).connection.commit()
            await interaction.response.edit_message(view=SendReactionRole(self.panel_id))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Error, There are no choices made for this panel.", color=discord.Color.red()), ephemeral=True)

    @button(label="Edit Embed", style=ButtonStyle.green, custom_id="edit_embed")
    async def EditEmbed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=EmbedEditButtons(self.panel_id))
    
    @button(label="Configure Choices", style=ButtonStyle.green, custom_id="config_choices")
    async def configChoices(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=ConfigureChoices(self.panel_id))
