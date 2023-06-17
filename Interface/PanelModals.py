import sqlite3
import discord
import datetime
from discord import TextStyle, ButtonStyle
from discord.ui import Modal, TextInput, View, ChannelSelect, select, button, Button, RoleSelect
from Interface.TicketButtons import TicketPanelButtons

class PanelChannelSelect(View):
    def __init__(self, panelID):
        self.panelID = panelID
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)
    
    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Select a Ticketing Channel', min_values=1, max_values=1)
    async def panelChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        total_embeds = []
        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name=embed.fields[1].name, value=select.values[0].mention)
        total_embeds.append(embed)
        self.database.execute(f"UPDATE TicketPanels SET channel_id = {select.values[0].id} WHERE panel_id = '{self.panelID}'")
        self.database.commit()

        data = self.database.execute(f"SELECT channel_id, category_id, role_id FROM TicketPanels WHERE panel_id = '{self.panelID}'").fetchone()
        if data[0] and data[1] and data[2]:
            self.createPanel.disabled = False

        if len(interaction.message.embeds) == 2:
            total_embeds.append(interaction.message.embeds[1])

        await interaction.response.edit_message(embeds=total_embeds, view=self)
    
    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.category], placeholder="Select Tickets Category", min_values=1, max_values=1)
    async def panelCategorySelect(self, interaction: discord.Interaction, select: ChannelSelect):
        total_embeds = []
        embed = interaction.message.embeds[0]
        embed.set_field_at(2, name=embed.fields[2].name, value=select.values[0].mention)
        total_embeds.append(embed)
        self.database.execute(f"UPDATE TicketPanels SET category_id = {select.values[0].id} WHERE panel_id = '{self.panelID}'")
        self.database.commit()
        
        data = self.database.execute(f"SELECT channel_id, category_id, role_id FROM TicketPanels WHERE panel_id = '{self.panelID}'").fetchone()
        if data[0] and data[1] and data[2]:
            self.createPanel.disabled = False
            
        if len(interaction.message.embeds) == 2:
            total_embeds.append(interaction.message.embeds[1])

        await interaction.response.edit_message(embeds=total_embeds, view=self)
    
    @select(cls=RoleSelect, placeholder="Select a role for Ticket Managers", min_values=1, max_values=1)
    async def panelRoleSelect(self, interaction: discord.Interaction, select: RoleSelect):
        total_embeds = []
        embed = interaction.message.embeds[0]
        embed.set_field_at(3, name=embed.fields[3].name, value=select.values[0].mention)
        total_embeds.append(embed)
        self.database.execute(f"UPDATE TicketPanels SET role_id = {select.values[0].id} WHERE panel_id = '{self.panelID}'")
        self.database.commit()

        data = self.database.execute(f"SELECT channel_id, category_id, role_id FROM TicketPanels WHERE panel_id = '{self.panelID}'").fetchone()
        if data[0] and data[1] and data[2]:
            self.createPanel.disabled = False
        
        if len(interaction.message.embeds) == 2:
            total_embeds.append(interaction.message.embeds[1])
        
        await interaction.response.edit_message(embeds=total_embeds, view=self)
    
    @button(label="Add Embed", style=ButtonStyle.blurple)
    async def addEmbed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(PanelCreate(self.panelID))
    
    @button(label="Create Panel", style=ButtonStyle.green, disabled=True)
    async def createPanel(self, interaction: discord.Interaction, button: Button):
        data = self.database.execute(f"SELECT channel_id FROM TicketPanels WHERE panel_id = '{self.panelID}'").fetchone()
        channel = interaction.guild.get_channel(data[0])
        if len(interaction.message.embeds) == 2:
            msg = await channel.send(embed=interaction.message.embeds[1], view=TicketPanelButtons())
            embed = interaction.message.embeds[0]
            embed.title = 'Panel Created'
            embed.clear_fields()
            embed.color.green()
            embed.description = f'New [Ticket Panel]({msg.jump_url}) has been created.'
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4315/4315445.png")
            self.database.execute(f"UPDATE TicketPanels SET message_id = {msg.id} WHERE panel_id = '{self.panelID}'")
            self.database.commit()
            await interaction.response.edit_message(embed=embed, view=None)

class PanelCreate(Modal, title="Create a New Ticket Panel"):
    def __init__(self, panelID):
        self.panelID = panelID
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    titleInput = TextInput(
        label="Title",
        style=TextStyle.short,
        placeholder="Panel title here",
        required=True
    )
    
    descInput = TextInput(
        label="Description",
        style=TextStyle.long,
        placeholder="Panel description here",
        required=True
    )

    colorInput = TextInput(
        label="Color",
        style=TextStyle.short,
        placeholder="Panel embed color HEX code here, e.g (#FF0000)",
        min_length=7,
        max_length=7,
        required=True
    )

    thumbInput = TextInput(
        label="Thumbnail",
        style=TextStyle.short,
        placeholder="Panel thumbnail url here",
        required=False
    )

    imageInput = TextInput(
        label="Image",
        style=TextStyle.short,
        placeholder="Panel image url here",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.titleInput,
            description=self.descInput,
            color=int(str(self.colorInput).replace('#', '0x'), 0),
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=self.thumbInput)
        embed.set_image(url=self.imageInput)

        old_embed = interaction.message.embeds[0]
        old_embed.set_field_at(0, name=old_embed.fields[0].name, value="Embed Added")
        
        await interaction.response.edit_message(embeds=[old_embed, embed])