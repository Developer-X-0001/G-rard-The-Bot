import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ext import commands
from discord.ui import View, ChannelSelect, RoleSelect, Button, select, button

database = sqlite3.connect("./Databases/settings.sqlite")

class CasesConfigView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Set Cases Channel!', min_values=1, max_values=1, row=0)
    async def CasesChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)
        database.execute("INSERT INTO CasesModuleSettings VALUES (?, ?, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET cases_channel = ? WHERE guild_id = ?", (interaction.guild.id, channel.id, channel.id, interaction.guild.id,)).connection.commit()

        config_embed = interaction.message.embeds[0]
        config_embed.set_field_at(
            index=0,
            name=config_embed.fields[0].name,
            value=channel.mention,
            inline=True
        )
        await interaction.response.edit_message(embed=config_embed, view=self)

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Set Cases Logs Channel!', min_values=1, max_values=1, row=1)
    async def CasesLogsChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)
        database.execute("INSERT INTO CasesModuleSettings VALUES (?, NULL, ?, NULL) ON CONFLICT (guild_id) DO UPDATE SET cases_log_channel = ? WHERE guild_id = ?", (interaction.guild.id, channel.id, channel.id, interaction.guild.id,)).connection.commit()

        config_embed = interaction.message.embeds[0]
        config_embed.set_field_at(
            index=1,
            name=config_embed.fields[1].name,
            value=channel.mention,
            inline=True
        )
        await interaction.response.edit_message(embed=config_embed, view=self)

    @select(cls=RoleSelect, placeholder="Select a role for case handlers", min_values=1, max_values=1, row=2)
    async def panelRoleSelect(self, interaction: discord.Interaction, select: RoleSelect):
        role = interaction.guild.get_role(select.values[0].id)
        database.execute("INSERT INTO CasesModuleSettings VALUES (?, NULL, NULL, ?) ON CONFLICT (guild_id) DO UPDATE SET cases_role = ? WHERE guild_id = ?", (interaction.guild.id, role.id, role.id, interaction.guild.id,)).connection.commit()

        config_embed = interaction.message.embeds[0]
        config_embed.set_field_at(
            index=2,
            name=config_embed.fields[2].name,
            value=role.mention,
            inline=True
        )
        await interaction.response.edit_message(embed=config_embed, view=self)


    @button(label="Done", style=ButtonStyle.green, row=3)
    async def cases_done(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)