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

        if panel_id_data is None or panel_id_data[0] is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Unable to get the Ticket channel/thread!**", color=discord.Color.red()), ephemeral=True)
            return

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
                await channel.send(content="{} {} **joined the ticket.**".format(config.JOINED_EMOJI, interaction.user.mention))
                await interaction.response.send_message(embed=discord.Embed(description="You've been connected to: {}".format(channel.mention), color=discord.Color.blue()), ephemeral=True)
            
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
        await interaction.response.defer()
        self._close.disabled = True
        self._close_with_reason.disabled = True
        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            ticket_data = self.database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
            ticket_author = interaction.guild.get_member(ticket_data[0])
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = False
            await interaction.channel.set_permissions(target=ticket_author, overwrite=permissions)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
            self.database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', interaction.channel.id,)).connection.commit()
            await interaction.followup.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()), view=TicketCloseButtons())
            return

        await thread.remove_user(interaction.user)

        await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        self.database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', interaction.channel.id,)).connection.commit()
        await interaction.followup.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()), view=TicketCloseButtons())

    @button(label="Close with reason", style=ButtonStyle.red, emoji="🔏", custom_id="ticket-close-with-reason")
    async def _close_with_reason(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CloseReasonModal(original_view=self))

class TicketCloseButtons(View):
    def __init__(self):
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)

    @button(label="Re-open", style=ButtonStyle.green, custom_id="ticket-reopen", row=0)
    async def _reopen(self, interaction: discord.Interaction, button: Button):
        old_ticket_data = self.database.execute("SELECT panel_id, log_message FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
        ticket_config_data = self.database.execute("SELECT log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        panel_data = self.database.execute("SELECT panel_title FROM TicketPanels WHERE panel_id = ?", (old_ticket_data[0],)).fetchone()

        try:
            log_channel = interaction.guild.get_channel(ticket_config_data[0])
            old_msg = log_channel.get_partial_message(old_ticket_data[1])
            await old_msg.delete()
        except:
            pass

        ticket_data = self.database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
        ticket_author = interaction.guild.get_member(ticket_data[0])
        await interaction.response.defer()
        
        self._reopen.disabled = True

        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = True
            permissions.send_messages = True
            permissions.read_message_history = True
            permissions.attach_files = True
            permissions.embed_links = True
            await interaction.channel.set_permissions(target=ticket_author, overwrite=permissions)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
            await interaction.followup.send(embed=discord.Embed(title="Ticket Re-Opened", description="{} just reopened this ticket.".format(interaction.user.mention), color=discord.Color.blue()), view=TicketChannelButtons())
            
            log_embed = discord.Embed(
                title="Join Ticket",
                description="A ticket has been opened. Press the button below to join it.",
                color=discord.Color.blue()
            )
            log_embed.add_field(
                name="Opened By",
                value=interaction.user.mention,
                inline=True
            )
            log_embed.add_field(
                name="Panel",
                value=panel_data[0],
                inline=True
            )
            log_embed.set_footer(text="Panel ID: {}".format(old_ticket_data[0]))

            log_msg = await log_channel.send(embed=log_embed, view=TicketLogButtons())
            self.database.execute("UPDATE UserTickets SET status = ?, log_message = ? WHERE channel_id = ?", ('open', log_msg.id, interaction.channel.id)).connection.commit()
            return

        await thread.add_user(ticket_author)
        await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        await interaction.followup.send(embed=discord.Embed(title="Ticket Re-Opened", description="{} just reopened this ticket.".format(interaction.user.mention), color=discord.Color.blue()), view=TicketChannelButtons())
        
        log_embed = discord.Embed(
            title="Join Ticket",
            description="A ticket has been opened. Press the button below to join it.",
            color=discord.Color.blue()
        )
        log_embed.add_field(
            name="Opened By",
            value=interaction.user.mention,
            inline=True
        )
        log_embed.add_field(
            name="Panel",
            value=panel_data[0],
            inline=True
        )
        log_embed.set_footer(text="Panel ID: {}".format(old_ticket_data[0]))

        log_msg = await log_channel.send(embed=log_embed, view=TicketLogButtons())
        self.database.execute("UPDATE UserTickets SET status = ?, log_message = ? WHERE channel_id = ?", ('open', log_msg.id, interaction.channel.id)).connection.commit()

    @button(label="Leave Ticket", style=ButtonStyle.red, custom_id="leave-ticket", row=0)
    async def _leave_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = False
            await interaction.channel.set_permissions(target=interaction.user, overwrite=permissions)
            await interaction.followup.send(content="{} {} **left the ticket.**".format(config.LEAVE_EMOJI, interaction.user.mention))
            return

        await thread.remove_user(interaction.user)

class CloseReasonModal(Modal, title="Ticket Close with Reason"):
    def __init__(self, original_view: TicketChannelButtons):
        self.original_view = original_view
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
        super().__init__(timeout=None)
    
    reason = TextInput(
        label="Reason",
        placeholder="Reason for closing the ticket.",
        style=TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.original_view._close.disabled = True
        self.original_view._close_with_reason.disabled = True
        thread = interaction.guild.get_thread(interaction.channel.id)
        if thread is None:
            ticket_data = self.database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
            ticket_author = interaction.guild.get_member(ticket_data[0])
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = False
            await interaction.channel.set_permissions(target=ticket_author, overwrite=permissions)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self.original_view)
            self.database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', interaction.channel.id,)).connection.commit()
            await interaction.followup.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}\n\n**Reason:**\n```\n{}\n```".format(interaction.user.mention, self.reason.value), color=discord.Color.blue()), view=TicketCloseButtons())
            return

        await thread.remove_user(interaction.user)

        await interaction.followup.edit_message(message_id=interaction.message.id, view=self.original_view)
        self.database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', interaction.channel.id,)).connection.commit()
        await interaction.followup.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}\n\n**Reason:**\n```\n{}\n```".format(interaction.user.mention, self.reason.value), color=discord.Color.blue()), view=TicketCloseButtons())