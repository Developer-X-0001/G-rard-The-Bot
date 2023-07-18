import config
import sqlite3
import discord

from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, Select, ChannelSelect, RoleSelect, Button, button, select

database = sqlite3.connect("./Databases/tickets.sqlite")

class TicketsConfigView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMethodSelector())
        self.add_item(TicketDMResponsesSelector())

    @select(cls=RoleSelect, placeholder="Set Ticket Manager Role", max_values=1, row=1)
    async def ticket_manager_select(self, interaction: discord.Interaction, select: RoleSelect):
        config_embed = interaction.message.embeds[0]
        manager_role = interaction.guild.get_role(select.values[0].id)

        config_embed.set_field_at(
            index=1,
            name=config_embed.fields[1].name,
            value=manager_role.mention,
            inline=True
        )

        database.execute("UPDATE TicketsConfig SET manager_role = ? WHERE guild_id = ?", (manager_role.id, interaction.guild.id,)).connection.commit()

        await interaction.response.edit_message(embed=config_embed)

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Set Ticket Logs Channel", max_values=1, row=2)
    async def ticket_log_channel_select(self, interaction: discord.Interaction, select: ChannelSelect):
        config_embed = interaction.message.embeds[0]
        log_channel = interaction.guild.get_channel(select.values[0].id)

        config_embed.set_field_at(
            index=3,
            name=config_embed.fields[3].name,
            value=log_channel.mention,
            inline=True
        )

        database.execute("UPDATE TicketsConfig SET log_channel = ? WHERE guild_id = ?", (log_channel.id, interaction.guild.id,)).connection.commit()

        await interaction.response.edit_message(embed=config_embed)

    @button(label="Done", style=ButtonStyle.green, row=4)
    async def done_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)

class TicketMethodSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Threads", description="Create tickets using threads.", value='threads'),
            discord.SelectOption(label="Channels", description="Create tickets using channels.", value="channels")
        ]

        super().__init__(placeholder="Select Ticketing Method", options=options, max_values=1, row=0)

    async def callback(self, interaction: discord.Interaction):
        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=0,
            name=config_embed.fields[0].name,
            value=self.values[0].capitalize(),
            inline=True
        )

        database.execute("UPDATE TicketsConfig SET ticket_method = ? WHERE guild_id = ?", (self.values[0], interaction.guild.id,)).connection.commit()

        await interaction.response.edit_message(embed=config_embed)

class TicketDMResponsesSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Enabled", description="DM users about ticket status.", value='enabled'),
            discord.SelectOption(label="Disabled", description="Don't DM users about ticket status.", value='disabled')
        ]
    
        super().__init__(placeholder="Configure DM Responses", options=options, max_values=1, row=3)
    
    async def callback(self, interaction: discord.Interaction):
        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=2,
            name=config_embed.fields[2].name,
            value=self.values[0].capitalize(),
            inline=True
        )

        database.execute("UPDATE TicketsConfig SET dm_responses = ? WHERE guild_id = ?", (self.values[0], interaction.guild.id,)).connection.commit()

        await interaction.response.edit_message(embed=config_embed)