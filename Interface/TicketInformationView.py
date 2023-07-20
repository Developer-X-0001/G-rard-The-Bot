import re
import config
import sqlite3
import discord

from discord import ButtonStyle
from Functions.ProcessEmbeds import process_embed
from discord.ui import Button, Select, View, button
from Interface.TicketButtons import TicketChannelButtons, TicketCloseButtons, TicketLogButtons

database = sqlite3.connect("./Databases/tickets.sqlite")

class TicketSelectorView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(TicketSelector(user_id=user_id))
    
class TicketSelector(Select):
    def __init__(self, user_id: int):
        options = []
        data = database.execute("SELECT panel_id, status, timestamp, channel_id FROM UserTickets WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()

        for entry in data:
            panel_info = database.execute("SELECT panel_title FROM TicketPanels WHERE panel_id = ?", (entry[0],)).fetchone()
            options.append(discord.SelectOption(label=f"{panel_info[0]} | {str(entry[1]).capitalize()}", description=f"Panel ID: {entry[0]}", value=entry[3]))
        
        super().__init__(placeholder="Select a ticket", max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        ticket_data = database.execute("SELECT panel_id, status, timestamp FROM UserTickets WHERE channel_id = ?", (self.values[0],)).fetchone()
        panel_info = database.execute("SELECT panel_title, panel_description FROM TicketPanels WHERE panel_id = ?", (ticket_data[0],)).fetchone()

        channel = interaction.guild.get_channel(int(self.values[0]))
        channel_or_thread = interaction.guild.get_channel_or_thread(int(self.values[0]))

        ticket_info_embed = discord.Embed(
            title=f"Ticket - {self.values[0]}",
            description=panel_info[1],
            color=discord.Color.blue()
        )
        ticket_info_embed.add_field(
            name="Category:",
            value=panel_info[0],
            inline=True
        )
        ticket_info_embed.add_field(
            name="Status:",
            value=str(ticket_data[1]).capitalize(),
            inline=True
        )
        ticket_info_embed.add_field(
            name="First Opened At:",
            value=f"<t:{ticket_data[2]}:f>",
            inline=True
        )
        ticket_info_embed.add_field(
            name="Ticket Type:",
            value=f"{config.THREAD_EMOJI} Thread" if channel is None else f"{config.CHANNEL_EMOJI} Channel",
            inline=True
        )
        if ticket_data[1] == 'open' and channel_or_thread is not None:
            ticket_info_embed.add_field(
                name="Jump URL:",
                value=f"[Ticket - {self.values[0]}]({channel_or_thread.jump_url})",
                inline=True
            )

        await interaction.response.edit_message(embed=ticket_info_embed, view=TicketOpenView(self.values[0]) if ticket_data[1] == 'open' else TicketCloseView(self.values[0]))
    
class TicketOpenView(View):
    def __init__(self, channel_id: int):
        self.channel_id = int(channel_id)
        super().__init__(timeout=None)
    
    @button(label="Close Ticket", style=ButtonStyle.red, row=0)
    async def ticket_close_btn(self, interaction: discord.Interaction, button: Button):
        thread = interaction.guild.get_thread(self.channel_id)
        if thread is None:
            channel = interaction.guild.get_channel(self.channel_id)
            ticket_data = database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (channel.id,)).fetchone()
            ticket_author = interaction.guild.get_member(ticket_data[0])
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = False
            await channel.set_permissions(target=ticket_author, overwrite=permissions)
            database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', self.channel_id,)).connection.commit()
            await channel.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()), view=TicketCloseButtons())
            ticket_embed = interaction.message.embeds[0]
            if ticket_embed.fields[4]:
                ticket_embed.remove_field(index=4)
            
            ticket_embed.set_field_at(
                index=1,
                name=ticket_embed.fields[1].name,
                value="Closed",
                inline=True
            )

            await interaction.response.edit_message(embed=ticket_embed, view=TicketCloseView(self.channel_id))
            return

        await thread.remove_user(interaction.user)
        database.execute("UPDATE UserTickets SET status = ? WHERE channel_id = ?", ('closed', self.channel_id,)).connection.commit()
        await thread.send(embed=discord.Embed(title="Ticket Closed", description="The ticket was closed by {}".format(interaction.user.mention), color=discord.Color.blue()), view=TicketCloseButtons())

        ticket_embed = interaction.message.embeds[0]
        if ticket_embed.fields[4]:
            ticket_embed.remove_field(index=4)
        
        ticket_embed.set_field_at(
            index=1,
            name=ticket_embed.fields[1].name,
            value="Closed",
            inline=True
        )

        await interaction.response.edit_message(embed=ticket_embed, view=TicketCloseView(self.channel_id))

    @button(label="Generate Transcript", style=ButtonStyle.blurple, emoji="📄", row=0)
    async def generate_transcript_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(content=f"{config.LOADING_EMOJI} **Generating Transcript...**", ephemeral=True)
        channel = interaction.guild.get_channel_or_thread(int(self.channel_id))

        if not channel:
            return "Channel not found."

        messages = []
        async for message in channel.history(limit=None):
            message_content = message.content

            # Replace Discord underline and bold with HTML tags
            message_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', message_content)
            message_content = re.sub(r'__(.*?)__', r'<u>\1</u>', message_content)

            # Check for embeds and process them
            if message.embeds:
                for embed in message.embeds:
                    message_content += await process_embed(embed)

            messages.append((message.author.name, message.author.id, message_content))

        if not messages:
            return "No messages found in this channel."

        transcript = "<!DOCTYPE html>\n<html>\n<head>\n<style>\n" \
                    "body { font-family: Arial, sans-serif; }\n" \
                    ".message { border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }\n" \
                    ".author { font-weight: bold; color: #007BFF; }\n" \
                    ".content { margin-top: 5px; }\n" \
                    "</style>\n</head>\n<body>\n"

        messages.reverse()

        for author_name, author_id, content in messages:
            transcript += f"<div class='message'>\n" \
                        f"<div class='author'>{author_name} ({author_id})</div>\n" \
                        f"<div class='content'>{content}</div>\n" \
                        f"</div>\n"

        transcript += "</body>\n</html>"

        try:
            with open(f"./Transcripts/transcript-{channel.id}.html", "w", encoding="utf-8") as file:
                file.write(transcript)
            
            await interaction.edit_original_response(content="✅ **Transcript Ready!**", view=TranscriptDownloadView(channel_id=channel.id))

        except Exception as e:
            return f"Error while generating the transcript: {e}"
        else:
            return "Ticket transcript generated successfully."

    @button(label="Go Back", style=ButtonStyle.gray, row=1)
    async def go_back_btn(self, interaction: discord.Interaction, button: Button):
        tickets_data = database.execute("SELECT panel_id, channel_id, status, timestamp FROM UserTickets WHERE user_id = ? ORDER BY timestamp DESC", (interaction.user.id,)).fetchall()

        open_tickets = ""
        closed_tickets = ""
        counter = 1

        for ticket in tickets_data:
            if ticket[2] == 'open':
                channel = interaction.guild.get_channel(ticket[1])
                if channel is None:
                    channel = interaction.guild.get_thread(ticket[1])
                open_tickets += f"{counter}. [{ticket[1]}]({channel.jump_url}) | <t:{ticket[3]}:R>\n"
                counter += 1
            else:
                closed_tickets += f"{counter}. {ticket[1]} | <t:{ticket[3]}:R>\n"
                counter += 1

        embed = discord.Embed(
            title="Your Ticket History",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Open Tickets:",
            value="No open tickets." if open_tickets == "" else open_tickets,
            inline=False
        )
        embed.add_field(
            name="Closed Tickets:",
            value="No closed tickets." if closed_tickets == "" else closed_tickets,
            inline=False
        )
        
        if open_tickets != "" or closed_tickets != "":
            await interaction.response.edit_message(embed=embed, view=TicketSelectorView(user_id=interaction.user.id))
            return
        
        await interaction.response.edit_message(embed=embed, view=None)

class TicketCloseView(View):
    def __init__(self, channel_id: int):
        self.channel_id = int(channel_id)
        super().__init__(timeout=None)
    
    @button(label="Re-Open Ticket", style=ButtonStyle.green, row=0)
    async def re_open_btn(self, interaction: discord.Interaction, button: Button):
        old_ticket_data = database.execute("SELECT panel_id, log_message FROM UserTickets WHERE channel_id = ?", (self.channel_id,)).fetchone()
        ticket_config_data = database.execute("SELECT log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        panel_data = database.execute("SELECT panel_title FROM TicketPanels WHERE panel_id = ?", (old_ticket_data[0],)).fetchone()

        try:
            log_channel = interaction.guild.get_channel(ticket_config_data[0])
            old_msg = log_channel.get_partial_message(old_ticket_data[1])
            await old_msg.delete()
        except:
            pass

        ticket_data = database.execute("SELECT user_id FROM UserTickets WHERE channel_id = ?", (self.channel_id,)).fetchone()
        ticket_author = interaction.guild.get_member(ticket_data[0])
    
        thread = interaction.guild.get_thread(self.channel_id)
        if thread is None:
            channel = interaction.guild.get_channel(self.channel_id)
            permissions = discord.PermissionOverwrite()
            permissions.view_channel = True
            permissions.send_messages = True
            permissions.read_message_history = True
            permissions.attach_files = True
            permissions.embed_links = True
            await channel.set_permissions(target=ticket_author, overwrite=permissions)
            await channel.send(embed=discord.Embed(title="Ticket Re-Opened", description="{} just reopened this ticket.".format(interaction.user.mention), color=discord.Color.blue()), view=TicketChannelButtons())
            
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
            database.execute("UPDATE UserTickets SET status = ?, log_message = ? WHERE channel_id = ?", ('open', log_msg.id, self.channel_id)).connection.commit()

            ticket_data = database.execute("SELECT panel_id, status, timestamp FROM UserTickets WHERE channel_id = ?", (self.channel_id,)).fetchone()

            channel_or_thread = interaction.guild.get_channel_or_thread(int(self.channel_id))

            ticket_embed = interaction.message.embeds[0]

            ticket_embed.set_field_at(
                index=1,
                name=ticket_embed.fields[1].name,
                value="Open",
                inline=True
            )

            if ticket_data[1] == 'closed' and channel_or_thread is not None:
                ticket_embed.add_field(
                    name="Jump URL:",
                    value=f"[Ticket - {channel_or_thread.id}]({channel_or_thread.jump_url})",
                    inline=True
                )

            await interaction.response.edit_message(embed=ticket_embed, view=TicketOpenView(self.channel_id))
            return

        await thread.add_user(ticket_author)
        await thread.send(embed=discord.Embed(title="Ticket Re-Opened", description="{} just reopened this ticket.".format(interaction.user.mention), color=discord.Color.blue()), view=TicketChannelButtons())

        ticket_data = database.execute("SELECT panel_id, status, timestamp FROM UserTickets WHERE channel_id = ?", (self.channel_id,)).fetchone()

        channel_or_thread = interaction.guild.get_channel_or_thread(int(self.channel_id))

        ticket_embed = interaction.message.embeds[0]

        ticket_embed.set_field_at(
            index=1,
            name=ticket_embed.fields[1].name,
            value="Open",
            inline=True
        )

        if ticket_data[1] == 'closed' and channel_or_thread is not None:
            ticket_embed.add_field(
                name="Jump URL:",
                value=f"[Ticket - {channel_or_thread.id}]({channel_or_thread.jump_url})",
                inline=True
            )

        await interaction.response.edit_message(embed=ticket_embed, view=TicketOpenView(self.channel_id))

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
        database.execute("UPDATE UserTickets SET status = ?, log_message = ? WHERE channel_id = ?", ('open', log_msg.id, self.channel_id)).connection.commit()

    @button(label="Generate Transcript", style=ButtonStyle.blurple, emoji="📄", row=0)
    async def generate_transcript_btn(self, interaction: discord.Interaction, button: Button):
        pass

    @button(label="Go Back", style=ButtonStyle.gray, row=1)
    async def go_back_btn(self, interaction: discord.Interaction, button: Button):
        tickets_data = database.execute("SELECT panel_id, channel_id, status, timestamp FROM UserTickets WHERE user_id = ? ORDER BY timestamp DESC", (interaction.user.id,)).fetchall()

        open_tickets = ""
        closed_tickets = ""
        counter = 1

        for ticket in tickets_data:
            if ticket[2] == 'open':
                channel = interaction.guild.get_channel(ticket[1])
                if channel is None:
                    channel = interaction.guild.get_thread(ticket[1])
                open_tickets += f"{counter}. [{ticket[1]}]({channel.jump_url}) | <t:{ticket[3]}:R>\n"
                counter += 1
            else:
                closed_tickets += f"{counter}. {ticket[1]} | <t:{ticket[3]}:R>\n"
            counter += 1

        embed = discord.Embed(
            title="Your Ticket History",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Open Tickets:",
            value="No open tickets." if open_tickets == "" else open_tickets,
            inline=False
        )
        embed.add_field(
            name="Closed Tickets:",
            value="No closed tickets." if closed_tickets == "" else closed_tickets,
            inline=False
        )
        
        if open_tickets != "" or closed_tickets != "":
            await interaction.response.edit_message(embed=embed, view=TicketSelectorView(user_id=interaction.user.id))
            return
        
        await interaction.response.edit_message(embed=embed, view=None)

class TranscriptDownloadView(View):
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        super().__init__(timeout=None)
    
    @button(label="Download Transcript", style=ButtonStyle.blurple)
    async def download_transcript_btn(self, interaction: discord.Interaction, button: Button):
        file = discord.File(fp=f"./Transcripts/transcript-{self.channel_id}.html")
        await interaction.response.send_message(content="📄 Download the file and open it in your Internet Browser.", file=file, ephemeral=True)