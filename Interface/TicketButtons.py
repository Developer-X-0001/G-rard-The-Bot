import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from discord.ui import View, Modal, TextInput, Button, button

# class TicketPanelButtons(View):
#     def __init__(self):
#         self.database = sqlite3.connect("./Databases/tickets.sqlite")
#         super().__init__(timeout=None)

#     @button(label="Create Ticket", style=ButtonStyle.blurple, emoji="🎫", custom_id='create-ticket')
#     async def createTicket(self, interaction: discord.Interaction, button: Button):
#         user_tickets = self.database.execute(
#             "SELECT panel_id, channel_id, status FROM UserTickets WHERE user_id = ?", (interaction.user.id,)
#         ).fetchall()

#         if user_tickets is not None:
#             for ticket in user_tickets:
#                 if ticket[2] == 'open':
#                     embed = discord.Embed(
#                         description=f"❌ You can't open more than one ticket!",
#                         color=discord.Color.red()
#                     )
#                     embed.set_footer(text="Close your priously opened tickets to open more tickets.")
#                     await interaction.response.send_message(embed=embed, ephemeral=True)
#                     return
            
#         data = self.database.execute(
#             f"SELECT panel_id, role_id, category_id FROM TicketPanels WHERE message_id = ?", (interaction.message.id,)).fetchone()
#         category = interaction.guild.get_channel(data[2])
#         role = interaction.guild.get_role(data[1])
#         permissions = {
#             interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
#             interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
#             interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
#             role: discord.PermissionOverwrite(
#                 view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True)
#         }
#         channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}-{interaction.user.discriminator}', category=category, overwrites=permissions)
#         self.database.execute("INSERT INTO UserTickets VALUES (?, ?, ?, ?, ?)",
#                             (data[0], interaction.user.id, channel.id, 'open', round(datetime.datetime.now().timestamp()),))
#         self.database.commit()
#         embed = discord.Embed(
#             title="New Ticket Opened",
#             description=f"Hey, {interaction.user.mention}.\nPlease wait until a ticket manager responds to your ticket, refrain from pinging staff members.",
#             color=discord.Color.blue(),
#             timestamp=datetime.datetime.now()
#         )
#         await interaction.response.send_message(content=f"Ticket Created: {channel.mention}", ephemeral=True)
#         await channel.send(content=f"{interaction.user.mention} {role.mention}", embed=embed, view=TicketChannelButtons())

class TicketLogButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)
    
    @button(label="Join Ticket", style=ButtonStyle.blurple, custom_id="join_ticket_btn")
    async def join_ticket_btn(self, interaction: discord.Interaction, button: Button):
        panel_id_data = self.database.execute("SELECT panel_id, channel_id FROM UserTickets WHERE log_message = ?", (interaction.message.id,)).fetchone()
        data = self.database.execute("SELECT panel_role FROM TicketPanels WHERE panel_id = ?", (panel_id_data[0],)).fetchone()
        role = interaction.guild.get_role(data[0])

        if role in interaction.user.roles:
            thread = interaction.guild.get_thread(panel_id_data[1])
            if thread is None:
                channel = interaction.guild.get_channel(panel_id_data[1])
                
                permissions = discord.PermissionOverwrite()
                permissions.view_channel = True
                permissions.send_messages = True
                permissions.read_message_history = True
                permissions.attach_files = True
                permissions.embed_links = True

                await channel.set_permissions(target=interaction.user, overwrite=permissions)
                ping_msg = await channel.send(content=interaction.user.mention)
                await interaction.response.send_message(embed=discord.Embed(description="You've been connected to: {}".format(channel.mention), color=discord.Color.blue()), ephemeral=True)
                await ping_msg.delete()
            
            else:
                await thread.add_user(interaction.user)
                await interaction.response.send_message(embed=discord.Embed(description="You've been connected to: {}".format(thread.mention), color=discord.Color.blue()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You aren't authorized to join that Ticket!**", color=discord.Color.red()), ephemeral=True)

class TicketChannelButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    @button(label="Close", style=ButtonStyle.red, emoji="🔒", custom_id="ticket-close")
    async def _close(self, interaction: discord.Interaction, button: Button):
        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            ticket_data = self.database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
            ticket_author = interaction.guild.get_member(ticket_data[0])
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = False
            await interaction.channel.set_permissions(target=ticket_author, overwrite=permissions)
            await interaction.response.send_message(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()))
            return

        await thread.edit(locked=True)
        await thread.remove_user(interaction.user)

        await interaction.response.send_message(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()))

    @button(label="Close with reason", style=ButtonStyle.red, emoji="🔏", custom_id="ticket-close-with-reason")
    async def _close_with_reason(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CloseReasonModal())

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

class CloseReasonModal(Modal, title="Ticket Close with Reason"):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)
    
    reason = TextInput(
        label="Reason",
        placeholder="Reason for closing the ticket.",
        style=TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            permissions = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
                interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
            }
            await interaction.channel.edit(overwrites=permissions)
            await interaction.response.send_message(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}\n**Reason:**\n```\n{}\n```".format(interaction.user.mention, self.reason.value), color=discord.Color.blue()))
            return

        await thread.edit(locked=True)
        await thread.remove_user(interaction.user)

        await interaction.response.send_message(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}\n**Reason:**\n```\n{}\n```".format(interaction.user.mention, self.reason.value), color=discord.Color.blue()))