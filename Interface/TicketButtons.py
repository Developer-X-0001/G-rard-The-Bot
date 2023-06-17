import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle
from discord.ui import View, button, Button


class TicketPanelButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    @button(label="Create Ticket", style=ButtonStyle.blurple, emoji="🎫", custom_id='create-ticket')
    async def createTicket(self, interaction: discord.Interaction, button: Button):
        user_tickets = self.database.execute(
            "SELECT panel_id, channel_id, status FROM UserTickets WHERE user_id = ?", (interaction.user.id,)
        ).fetchall()

        if user_tickets is not None:
            for ticket in user_tickets:
                if ticket[2] == 'open':
                    embed = discord.Embed(
                        description=f"❌ You can't open more than one ticket!",
                        color=discord.Color.red()
                    )
                    embed.set_footer(text="Close your priously opened tickets to open more tickets.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
        data = self.database.execute(
            f"SELECT panel_id, role_id, category_id FROM TicketPanels WHERE message_id = ?", (interaction.message.id,)).fetchone()
        category = interaction.guild.get_channel(data[2])
        role = interaction.guild.get_role(data[1])
        permissions = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
            interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
            role: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True)
        }
        channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}-{interaction.user.discriminator}', category=category, overwrites=permissions)
        self.database.execute("INSERT INTO UserTickets VALUES (?, ?, ?, ?, ?)",
                            (data[0], interaction.user.id, channel.id, 'open', round(datetime.datetime.now().timestamp()),))
        self.database.commit()
        embed = discord.Embed(
            title="New Ticket Opened",
            description=f"Hey, {interaction.user.mention}.\nPlease wait until a ticket manager responds to your ticket, refrain from pinging staff members.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(content=f"Ticket Created: {channel.mention}", ephemeral=True)
        await channel.send(content=f"{interaction.user.mention} {role.mention}", embed=embed, view=TicketChannelButtons())

class TicketChannelButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    @button(label="Close", style=ButtonStyle.red, emoji="🔒", custom_id="ticket-close")
    async def _close(self, interaction: discord.Interaction, button: Button):
        self._close.disabled = True
        await interaction.response.edit_message(view=self)
        panel_data = self.database.execute(
            "SELECT panel_id, user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
        data = self.database.execute(
            "SELECT role_id FROM TicketPanels WHERE panel_id = ?", (panel_data[0],)).fetchone()

        user = interaction.guild.get_member(panel_data[1])
        role = interaction.guild.get_role(data[0])

        permissions = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
            role: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True)
        }

        close_embed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        await interaction.channel.send(embed=close_embed, view=TicketCloseButtons())
        await interaction.channel.edit(name=f"closed-{user.name}-{user.discriminator}", overwrites=permissions)
        self.database.execute(
            "UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', interaction.channel.id,))
        self.database.commit()


class TicketCloseButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    @button(label="Re-open", style=ButtonStyle.green, custom_id="ticket-reopen", row=0)
    async def _reopen(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        ticket_data = self.database.execute(
            "SELECT panel_id, user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
        panel_data = self.database.execute(
            "SELECT role_id FROM TicketPanels WHERE panel_id = ?", (ticket_data[0],)).fetchone()

        user = interaction.guild.get_member(ticket_data[1])
        role = interaction.guild.get_role(panel_data[0])

        permissions = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
            interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
            role: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True)
        }

        await interaction.channel.edit(name=f"ticket-{user.name}-{user.discriminator}", overwrites=permissions)
        await interaction.message.delete()
        embed = discord.Embed(
            title="Ticket Re-Opened",
            description=f"Hey, {interaction.user.mention}.\nPlease wait until a ticket manager responds to your ticket, refrain from pinging staff members.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        await interaction.channel.send(content=f"{user.mention} {role.mention}", embed=embed, view=TicketChannelButtons())
        self.database.execute(
            "UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('open', interaction.channel.id,))
        self.database.commit()

    @button(label="Delete", style=ButtonStyle.red, custom_id="ticket-delete", row=0)
    async def _delete(self, interaction: discord.Interaction, button: Button):
        await interaction.channel.delete()
        self.database.execute(
            "DELETE FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,))
        self.database.commit()