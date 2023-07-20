import config
import sqlite3
import discord

from discord import ButtonStyle, TextInput
from discord.ui import Button, Modal, TextInput, View, button

database = sqlite3.connect("./Databases/activity.sqlite")

class ActivityConfigView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Set Invite Points", style=ButtonStyle.blurple, row=0)
    async def invite_points_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetInvitePointsModal())

    @button(label="Set Message Points", style=ButtonStyle.blurple, row=0)
    async def message_points_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetMessagePointsModal())

    @button(label="Set Role Points", style=ButtonStyle.blurple, row=1)
    async def role_points_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetRolePointsModal())

    @button(label="Set Channel Points", style=ButtonStyle.blurple, row=1)
    async def channel_points_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetChannelPointsModal())

    @button(label="Set Points for Role & Channel", style=ButtonStyle.blurple, row=2)
    async def role_channel_points_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetRoleAndChannelPointsModal())

    @button(label="Done", style=ButtonStyle.green, row=3)
    async def done_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)

class SetInvitePointsModal(Modal, title="Set Invite Points"):
    def __init__(self):
        super().__init__(timeout=None)
    
    invite_points = TextInput(
        label="Invite Points",
        placeholder="Type a positive integer",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.invite_points.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Points value must be an Integer!**", color=discord.Color.red()), ephemeral=True)
            return

        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=0,
            name=config_embed.fields[0].name,
            value=self.invite_points.value,
            inline=False
        )

        database.execute("UPDATE ActivityConfig SET invitepoints = ? WHERE guild_id = ?", (int(self.invite_points.value), interaction.guild.id,)).connection.commit()
        await interaction.response.edit_message(embed=config_embed)

class SetMessagePointsModal(Modal, title="Set Message Points"):
    def __init__(self):
        super().__init__(timeout=None)
    
    message_points = TextInput(
        label="Message Points",
        placeholder="Type a positive integer",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.message_points.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Points value must be an Integer!**", color=discord.Color.red()), ephemeral=True)
            return

        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=1,
            name=config_embed.fields[1].name,
            value=self.message_points.value,
            inline=False
        )

        database.execute("UPDATE ActivityConfig SET invitepoints = ? WHERE guild_id = ?", (int(self.message_points.value), interaction.guild.id,)).connection.commit()
        await interaction.response.edit_message(embed=config_embed)

class SetRolePointsModal(Modal, title="Set Role Points"):
    def __init__(self):
        super().__init__(timeout=None)
    
    role_points = TextInput(
        label="Role Points",
        placeholder="Type a positive integer",
        required=True
    )

    role_id = TextInput(
        label="Role ID",
        placeholder="Type role id",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.role_points.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Points value must be an Integer!**", color=discord.Color.red()), ephemeral=True)
            return
    
        role = interaction.guild.get_role(int(self.role_id.value))
        if role is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Type a valid role ID!**", color=discord.Color.red()), ephemeral=True)
            return

        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=2,
            name=config_embed.fields[2].name,
            value=f"Role: {role.mention}\n"
                    f"Points: {self.role_points.value}",
            inline=False
        )

        database.execute("UPDATE ActivityConfig SET rolepoints = ?, role_id = ? WHERE guild_id = ?", (int(self.role_points.value), int(self.role_id.value), interaction.guild.id,)).connection.commit()
        await interaction.response.edit_message(embed=config_embed)

class SetChannelPointsModal(Modal, title="Set Channel Points"):
    def __init__(self):
        super().__init__(timeout=None)
    
    channel_points = TextInput(
        label="Role Points",
        placeholder="Type a positive integer",
        required=True
    )

    channel_id = TextInput(
        label="Role ID",
        placeholder="Type role id",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.channel_points.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Points value must be an Integer!**", color=discord.Color.red()), ephemeral=True)
            return
    
        channel = interaction.guild.get_role(int(self.channel_id.value))
        if channel is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Type a valid channel ID!**", color=discord.Color.red()), ephemeral=True)
            return

        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=3,
            name=config_embed.fields[3].name,
            value=f"Channel: {channel.mention}\n"
                    f"Points: {self.channel_points.value}",
            inline=False
        )

        database.execute("UPDATE ActivityConfig SET channelpoints = ?, channel_id = ? WHERE guild_id = ?", (int(self.channel_points.value), int(self.channel_id.value), interaction.guild.id,)).connection.commit()
        await interaction.response.edit_message(embed=config_embed)

class SetRoleAndChannelPointsModal(Modal, title="Set Points for Role & Channel"):
    def __init__(self):
        super().__init__(timeout=None)
    
    points = TextInput(
        label="Role Points",
        placeholder="Type a positive integer",
        required=True
    )

    role_id = TextInput(
        label="Role ID",
        placeholder="Type role id",
        required=True
    )

    channel_id = TextInput(
        label="Channel ID",
        placeholder="Type channel id",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.points.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Points value must be an Integer!**", color=discord.Color.red()), ephemeral=True)
            return

        role = interaction.guild.get_role(int(self.role_id.value))
        if role is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Type a valid role ID!**", color=discord.Color.red()), ephemeral=True)
            return
        
        channel = interaction.guild.get_channel(int(self.channel_id.value))
        if channel is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Type a valid channel ID!**", color=discord.Color.red()), ephemeral=True)
            return

        config_embed = interaction.message.embeds[0]

        config_embed.set_field_at(
            index=4,
            name=config_embed.fields[4].name,
            value=f"Role: {role.mention}\n"
                    f"Channel: {channel.mention}\n"
                    f"Points: {self.points.value}",
            inline=False
        )

        database.execute("UPDATE ActivityConfig SET roleandchannelpoints = ?, role_channel_id = ?, channel_role_id = ? WHERE guild_id = ?", (int(self.points.value), role.id, channel.id, interaction.guild.id,)).connection.commit()
        await interaction.response.edit_message(embed=config_embed)