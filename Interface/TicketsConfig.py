import emoji
import config
import string
import random
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from Functions.EmojiCheck import isUnicodeEmoji
from Functions.ColorChecks import isValidHexCode, hex_to_int
from Interface.TicketButtons import TicketChannelButtons, TicketLogButtons
from discord.ui import View, Select, Modal, TextInput, ChannelSelect, RoleSelect, Button, button, select

database = sqlite3.connect("./Databases/tickets.sqlite")

class TicketsConfigView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMethodSelector())
        self.add_item(TicketDMResponsesSelector())

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Set Ticket Logs Channel", max_values=1, row=2)
    async def ticket_log_channel_select(self, interaction: discord.Interaction, select: ChannelSelect):
        config_embed = interaction.message.embeds[0]
        log_channel = interaction.guild.get_channel(select.values[0].id)

        config_embed.set_field_at(
            index=2,
            name=config_embed.fields[2].name,
            value=log_channel.mention,
            inline=True
        )

        database.execute("UPDATE TicketsConfig SET log_channel = ? WHERE guild_id = ?", (log_channel.id, interaction.guild.id,)).connection.commit()

        await interaction.response.edit_message(embed=config_embed)

    @button(label="Done", style=ButtonStyle.green, row=4)
    async def done_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)

    @button(label="Edit Ticket Panels", style=ButtonStyle.blurple, row=4)
    async def edit_panels_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=discord.Embed(description="Here you can edit or configure your Ticket Panels", color=discord.Color.blue()), view=EditPanelsView())

    @button(label="Create Ticket Menu Message", style=ButtonStyle.blurple, row=4)
    async def create_ticket_message(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji FROM TicketPanels").fetchall()
        complete_panels = 0
        if data != []:
            for entry in data:
                if entry[0] and entry[1] and entry[2]:
                    complete_panels += 1
        
        if complete_panels == 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **There must be one fully functional panel to create a menu message!**", color=discord.Color.red()), ephemeral=True)
            return
        
        msg_embed = discord.Embed(
            title="<No Title Added>",
            description="<No Description Added>",
            color=0x000000
        )

        await interaction.response.edit_message(embed=msg_embed, view=CreateMessageView())

class CreateMessageSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Select a Channel", row=0)
    async def create_msg_channel_select(self, interaction: discord.Interaction, select: ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)

        ticket_msg = await channel.send(embed=interaction.message.embeds[0], view=GeneratePanelView())
        await interaction.response.edit_message(embed=discord.Embed(description="✅ Successfully created a [message]({}) with ticket panels.".format(ticket_msg.jump_url), color=discord.Color.green()), view=None)
    
    @button(label="Go Back", style=ButtonStyle.gray)
    async def create_msg_go_back_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=CreateMessageView())

class GeneratePanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GeneratePanelSelector())
    
class GeneratePanelSelector(Select):
    def __init__(self):
        options = []
        data = database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji FROM TicketPanels").fetchall()
        if data != []:
            for entry in data:
                if entry[0] and entry[1] and entry[2]:
                    options.append(discord.SelectOption(label=entry[1], description=entry[2], emoji=None if not entry[3] else entry[3], value=entry[0]))
                else:
                    pass

        super().__init__(placeholder="No Panels Found" if options == [] else "Select a Support Category", options=options, disabled=True if len(options) == 0 else False, row=0, custom_id="ticket_panel_selector")
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT ticket_method, log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if not data:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Ticketing System isn't correctly configured!**", color=discord.Color.red()), ephemeral=True)
            return

        if data[0] == 'threads':
            tickets_data = database.execute("SELECT * FROM UserTickets WHERE user_id = ? AND status = ?", (interaction.user.id, 'open')).fetchall()
            panel_data = database.execute("SELECT panel_title, panel_limit FROM TicketPanels WHERE panel_id = ?", (self.values[0],)).fetchone()

            if tickets_data:
                if len(tickets_data) >= int(panel_data[1]):
                    await interaction.response.send_message(embed=discord.Embed(description="❌ **You've opened maximum available tickets from this category!**", color=discord.Color.red()).set_footer(text="Close your previous tickets to open new tickets."), ephemeral=True)
                    return

            channel = interaction.channel
            log_channel = interaction.guild.get_channel(data[1])
            ticket_thread = await channel.create_thread(name="ticket-{}".format(interaction.user.name), invitable=True)
            await ticket_thread.add_user(interaction.user)
            await ticket_thread.send(embed=discord.Embed(title=panel_data[0], description="Thank you for contacting our support.\nPlease describe your issue and await a response.", color=discord.Color.blue()), view=TicketChannelButtons())
            
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send(embed=discord.Embed(title="Ticket - {}".format(panel_data[0]), description="Opened a new ticket: {}".format(channel.mention), color=discord.Color.blue()), ephemeral=True)

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
            log_embed.set_footer(text="Panel ID: {}".format(self.values[0]))

            log_msg = await log_channel.send(embed=log_embed, view=TicketLogButtons())

            database.execute("INSERT INTO UserTickets VALUES (?, ?, ?, ?, ?, ?)", (self.values[0], interaction.user.id, ticket_thread.id, 'open', round(datetime.datetime.now().timestamp()), log_msg.id,)).connection.commit()

        if data[0] == 'channels':
            tickets_data = database.execute("SELECT * FROM UserTickets WHERE user_id = ? AND status = ?", (interaction.user.id, 'open')).fetchall()
            panel_data = database.execute("SELECT panel_title, panel_role, panel_category, panel_limit FROM TicketPanels WHERE panel_id = ?", (self.values[0],)).fetchone()

            if tickets_data:
                if len(tickets_data) >= int(panel_data[3]):
                    await interaction.response.send_message(embed=discord.Embed(description="❌ **You've opened maximum available tickets from this category!**", color=discord.Color.red()).set_footer(text="Close your previous tickets to open new tickets."), ephemeral=True)
                    return
                
            category = interaction.guild.get_channel(panel_data[2])
            if not category:
                await interaction.response.send_message(embed=discord.Embed(description="❌ **No category set for this option!**", color=discord.Color.red()), ephemeral=True)
                return
            
            log_channel = interaction.guild.get_channel(data[1])
            permissions = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
                interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True, manage_messages=True, manage_channels=True),
            }
            channel = await interaction.guild.create_text_channel(name=f'ticket-{interaction.user.name}', category=category, overwrites=permissions)

            await channel.send(content=interaction.user.mention, embed=discord.Embed(title=panel_data[0], description="Thank you for contacting our support.\nPlease describe your issue and await a response.", color=discord.Color.blue()), view=TicketChannelButtons())
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send(embed=discord.Embed(title="Ticket - {}".format(panel_data[0]), description="Opened a new ticket: {}".format(channel.mention), color=discord.Color.blue()), ephemeral=True)

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
            log_embed.set_footer(text="Panel ID: {}".format(self.values[0]))

            log_msg = await log_channel.send(embed=log_embed, view=TicketLogButtons())

            database.execute("INSERT INTO UserTickets VALUES (?, ?, ?, ?, ?, ?)", (self.values[0], interaction.user.id, channel.id, 'open', round(datetime.datetime.now().timestamp()), log_msg.id,)).connection.commit()

class CreateMessageView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Edit Embed", style=ButtonStyle.blurple)
    async def edit_embed_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EditEmbedModal())

    @button(label="Create Message", style=ButtonStyle.blurple)
    async def create_msg_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=CreateMessageSelectorView())

    @button(label="Go Back", style=ButtonStyle.gray)
    async def go_back_btn_3(self, interaction: discord.Interaction, button: Button):
        config_embed = discord.Embed(
            title="Ticket System Configuration",
            color=discord.Color.blue()
        )

        data = database.execute("SELECT ticket_method, dm_responses, log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        panels_data = database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji, panel_role, panel_category FROM TicketPanels").fetchall()
        if data is None:
            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="DM Responses",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="Log Channel",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="Ticket Panels",
                value="No Panels Found",
                inline=False
            )
            await interaction.response.send_message(embed=config_embed, view=TicketsConfigView(), ephemeral=True)
            
        else:
            panels_info = ""
            if panels_data != []:
                full_panels = 0
                missing_panels = 0
                for panel in panels_data:
                    if panel[0] and panel[1] and panel[2] and panel[4] and panel[5]:
                        full_panels += 1
                    else:
                        missing_panels += 1
                
                panels_info = "{} Panels Functional\n{} Panels Incomplete".format(full_panels, missing_panels)

            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured" if not data[0] else f"{f'{config.CHANNEL_EMOJI} ' if data[0] == 'channels' else f'{config.THREAD_EMOJI} '}{data[0].capitalize()}",
                inline=True
            )
            config_embed.add_field(
                name="DM Responses",
                value="Not Configured" if not data[1] else data[1].capitalize(),
                inline=True
            )
            config_embed.add_field(
                name="Log Channel",
                value="Not Configured" if not data[2] else interaction.guild.get_channel(data[2]).mention,
                inline=True
            )
            config_embed.add_field(
                name=f"Ticket Panels [{len(panels_data)}]",
                value=f"{len(panels_data)} Panels Found\n\n{panels_info}",
                inline=False
            )
            await interaction.response.edit_message(embed=config_embed, view=TicketsConfigView())

class EditPanelsView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Go Back", style=ButtonStyle.gray, row=2)
    async def go_back_btn(self, interaction: discord.Interaction, button: Button):
        config_embed = discord.Embed(
            title="Ticket System Configuration",
            color=discord.Color.blue()
        )

        data = database.execute("SELECT ticket_method, dm_responses, log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        panels_data = database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji, panel_role, panel_category FROM TicketPanels").fetchall()
        if data is None:
            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="DM Responses",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="Log Channel",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="Ticket Panels",
                value="No Panels Found",
                inline=False
            )
            await interaction.response.send_message(embed=config_embed, view=TicketsConfigView(), ephemeral=True)
            
        else:
            panels_info = ""
            if panels_data != []:
                full_panels = 0
                missing_panels = 0
                for panel in panels_data:
                    if panel[0] and panel[1] and panel[2] and panel[4] and panel[5]:
                        full_panels += 1
                    else:
                        missing_panels += 1
                
                panels_info = "{} Panels Functional\n{} Panels Incomplete".format(full_panels, missing_panels)

            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured" if not data[0] else f"{f'{config.CHANNEL_EMOJI} ' if data[0] == 'channels' else f'{config.THREAD_EMOJI} '}{data[0].capitalize()}",
                inline=True
            )
            config_embed.add_field(
                name="DM Responses",
                value="Not Configured" if not data[1] else data[1].capitalize(),
                inline=True
            )
            config_embed.add_field(
                name="Log Channel",
                value="Not Configured" if not data[2] else interaction.guild.get_channel(data[2]).mention,
                inline=True
            )
            config_embed.add_field(
                name=f"Ticket Panels [{len(panels_data)}]",
                value=f"{len(panels_data)} Panels Found\n\n{panels_info}",
                inline=False
            )
            await interaction.response.edit_message(embed=config_embed, view=TicketsConfigView())

    @button(label="Create a new Ticket Panel", style=ButtonStyle.blurple, row=1)
    async def new_panel_btn(self, interaction: discord.Interaction, button: Button):
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(7)]).upper()

        new_panel_embed = discord.Embed(
            title="Creating a new Ticket Panel",
            color=discord.Color.blue()
        )
        new_panel_embed.add_field(
            name="Panel Title:",
            value="N/A",
            inline=False
        )
        new_panel_embed.add_field(
            name="Panel Description:",
            value="N/A",
            inline=False
        )
        new_panel_embed.add_field(
            name="Panel Emoji:",
            value="N/A",
            inline=False
        )
        new_panel_embed.add_field(
            name="Panel Manager Role:",
            value="N/A",
            inline=False
        )
        new_panel_embed.add_field(
            name="Ticket Category: (If using Channels method)",
            value="N/A",
            inline=False
        )
        new_panel_embed.add_field(
            name="Panel Ticket Limit:",
            value="3",
            inline=False
        )
        
        database.execute("INSERT INTO TicketPanels VALUES (?, NULL, NULL, NULL, NULL, NULL, ?)", (id, 3,)).connection.commit()
        await interaction.response.edit_message(embed=new_panel_embed, view=CreatePanelsView(panel_id=id))
    
    @button(label="Edit Existing Panels", style=ButtonStyle.blurple, row=1)
    async def edit_panels_btn(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT * FROM TicketPanels").fetchall()
        if data == []:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **There aren't any panels created yet.**", color=discord.Color.red()), ephemeral=True)
            return

        await interaction.response.edit_message(embed=discord.Embed(description="Select a Ticket panel to edit its information.", color=discord.Color.blue()), view=EditExistingPanelsView())

class CreatePanelsView(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)

    @select(cls=RoleSelect, placeholder="Set Ticket Manager Role", max_values=1, row=0)
    async def ticket_manager_select(self, interaction: discord.Interaction, select: RoleSelect):
        new_panel_embed = interaction.message.embeds[0]
        manager_role = interaction.guild.get_role(select.values[0].id)

        new_panel_embed.set_field_at(
            index=3,
            name=new_panel_embed.fields[3].name,
            value=manager_role.mention,
            inline=True
        )

        database.execute("UPDATE TicketPanels SET panel_role = ? WHERE panel_id = ?", (manager_role.id, self.panel_id,)).connection.commit()

        await interaction.response.edit_message(embed=new_panel_embed)

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.category], placeholder="Select Ticket Category", max_values=1, row=1)
    async def ticket_cat_select(self, interaction: discord.Interaction, select: ChannelSelect):
        new_panel_embed = interaction.message.embeds[0]
        ticket_category = interaction.guild.get_channel(select.values[0].id)

        new_panel_embed.set_field_at(
            index=4,
            name=new_panel_embed.fields[4].name,
            value=ticket_category.mention,
            inline=False
        )

        database.execute("UPDATE TicketPanels SET panel_category = ? WHERE panel_id = ?", (ticket_category.id, self.panel_id,)).connection.commit()

        await interaction.response.edit_message(embed=new_panel_embed)

    @button(label="Edit Panel Information", style=ButtonStyle.blurple, row=2)
    async def edit_panel_info_btn(self, interaction: discord.Interaction, button: Button):
        new_panel_embed = interaction.message.embeds[0]
        title = new_panel_embed.fields[0].value
        desc = new_panel_embed.fields[1].value
        emoji = new_panel_embed.fields[2].value
        limit = int(new_panel_embed.fields[5].value)
        await interaction.response.send_modal(NewPanelModal(panel_id=self.panel_id, title=None if title == 'N/A' else title, description=None if desc == 'N/A' else desc, emoji=None if emoji == 'N/A' else emoji, limit=limit))

    @button(label="Delete Panel", style=ButtonStyle.red)
    async def delete_panel_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        database.execute("DELETE FROM TicketPanels WHERE panel_id = ?", (self.panel_id,)).connection.commit()
        data = database.execute("SELECT * FROM TicketPanels").fetchall()
        embed = interaction.message.embeds[0]
        if len(data) > 0 and embed.title == "Editing a Ticket Panel":
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(description="Select a Ticket panel to edit its information.", color=discord.Color.blue()), view=EditExistingPanelsView())
            return
        
        await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(description="Here you can edit or configure your Ticket Panels", color=discord.Color.blue()), view=EditPanelsView())
        await interaction.followup.send(embed=discord.Embed(description="✅ Ticket Panel with ID `{}` has been deleted.".format(self.panel_id), color=discord.Color.green()), ephemeral=True)

    @button(label="Go Back", style=ButtonStyle.gray, row=3)
    async def create_panels_back_btn(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        if embed.title == "Editing a Ticket Panel":
            await interaction.response.edit_message(embed=discord.Embed(description="Select a Ticket panel to edit its information.", color=discord.Color.blue()), view=EditExistingPanelsView())
            return
        
        await interaction.response.edit_message(embed=discord.Embed(description="Here you can edit or configure your Ticket Panels", color=discord.Color.blue()), view=EditPanelsView())

class EditExistingPanelsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PanelsSelector())
    
    @button(label="Go Back", style=ButtonStyle.gray, row=1)
    async def edit_panels_back_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=discord.Embed(description="Here you can edit or configure your Ticket Panels", color=discord.Color.blue()), view=EditPanelsView())

class PanelsSelector(Select):
    def __init__(self):
        options = []
        data = database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji FROM TicketPanels").fetchall()
        if data != []:
            for entry in data:
                if entry[0] and entry[1] and entry[2]:
                    options.append(discord.SelectOption(label=entry[1], description=entry[2], emoji=None if not entry[3] else entry[3], value=entry[0]))
                else:
                    options.append(discord.SelectOption(label="No Title (Incomplete Panel)" if not entry[1] else entry[1], description="No Description" if not entry[2] else entry[2], emoji=None if not entry[3] else entry[3], value=entry[0]))

        super().__init__(placeholder="No Panels Found" if options == [] else "Select a Ticketing Panel", options=options, disabled=True if len(options) == 0 else False, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT panel_title, panel_description, panel_emoji, panel_role, panel_category, panel_limit FROM TicketPanels WHERE panel_id = ?", (self.values[0],)).fetchone()
        role = interaction.guild.get_role(data[3])
        category = interaction.guild.get_channel(data[4])

        panel_embed = discord.Embed(
            title="Editing a Ticket Panel",
            color=discord.Color.blue()
        )
        panel_embed.add_field(
            name="Panel Title:",
            value="N/A" if not data[0] else data[0],
            inline=False
        )
        panel_embed.add_field(
            name="Panel Description:",
            value="N/A" if not data[1] else data[1],
            inline=False
        )
        panel_embed.add_field(
            name="Panel Emoji:",
            value="N/A" if not data[2] else data[2],
            inline=False
        )
        panel_embed.add_field(
            name="Panel Manager Role:",
            value="N/A" if role is None else role.mention,
            inline=False
        )
        panel_embed.add_field(
            name="Ticket Category: (If using Channel method)",
            value="N/A" if category is None else category.mention,
            inline=False
        )
        panel_embed.add_field(
            name="Panel Ticket Limit:",
            value="3" if not data[5] else data[5],
            inline=False
        )

        await interaction.response.edit_message(embed=panel_embed, view=CreatePanelsView(panel_id=self.values[0]))

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
            value=f"{f'{config.CHANNEL_EMOJI} ' if self.values[0] == 'channels' else f'{config.THREAD_EMOJI} '}{self.values[0].capitalize()}",
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
    
        super().__init__(placeholder="Configure DM Responses", options=options, max_values=1, row=1)
    
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

class NewPanelModal(Modal, title="New Ticket Panel Modal"):
    def __init__(self, panel_id: str, title: str=None, description: str=None, emoji: str=None, limit: int=None):
        self.panel_id = panel_id
        self._title = title
        self._description = description
        self._emoji = emoji
        self._limit = limit
        super().__init__(timeout=None)
    
        self.panel_title = TextInput(
            label="Panel Title",
            placeholder="Type a title for the panel",
            max_length=100,
            style=TextStyle.short,
            default=self._title,
            required=True
        )

        self.panel_description = TextInput(
            label="Panel Description",
            placeholder="Type a brief description of the panel",
            max_length=100,
            default=self._description,
            style=TextStyle.short,
            required=True
        )

        self.panel_emoji = TextInput(
            label="Panel Emoji",
            placeholder="UNICODE EMOJI ONLY! (Optional)",
            style=TextStyle.short,
            default=self._emoji,
            required=False
        )
        
        self.panel_limit = TextInput(
            label="Panel Ticket Limit",
            placeholder="Type a positive Integer",
            style=TextStyle.short,
            default=self._limit,
            max_length=2,
            required=True
        )

        self.add_item(self.panel_title)
        self.add_item(self.panel_description)
        self.add_item(self.panel_emoji)
        self.add_item(self.panel_limit)

    async def on_submit(self, interaction: discord.Interaction):
        if self.panel_emoji.value:
            emojized = emoji.emojize(self.panel_emoji.value)
            if not isUnicodeEmoji(character=emojized):
                await interaction.response.send_message(embed=discord.Embed(description="❌ **Only UNICODE emoji are allowed!**\nPress `Windows + .` to view UNICODE emojis.", color=discord.Color.red()), ephemeral=True)
                return
        
        if not self.panel_limit.value.isdigit():
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Ticket Limit must be a valid Integer!**", color=discord.Color.red()), ephemeral=True)
            return

        if self.panel_limit.value.isdigit() and int(self.panel_limit.value) <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Ticket Limit must be greater than `0`!**", color=discord.Color.red()), ephemeral=True)
            return
    
        new_panel_embed = interaction.message.embeds[0]

        new_panel_embed.set_field_at(
            index=0,
            name=new_panel_embed.fields[0].name,
            value=self.panel_title.value,
            inline=False
        )
        new_panel_embed.set_field_at(
            index=1,
            name=new_panel_embed.fields[1].name,
            value=self.panel_description.value,
            inline=False
        )
        new_panel_embed.set_field_at(
            index=2,
            name=new_panel_embed.fields[2].name,
            value="N/A" if not self.panel_emoji.value else self.panel_emoji.value,
            inline=False
        )
        new_panel_embed.set_field_at(
            index=5,
            name=new_panel_embed.fields[5].name,
            value="3" if not self.panel_limit.value else self.panel_limit.value,
            inline=False
        )

        database.execute("UPDATE TicketPanels SET panel_title = ?, panel_description = ?, panel_emoji = ?, panel_limit = ? WHERE panel_id = ?", (self.panel_title.value, self.panel_description.value, None if not self.panel_emoji.value else self.panel_emoji.value, 3 if not self.panel_limit.value else self.panel_limit.value, self.panel_id,)).connection.commit()
        await interaction.response.edit_message(embed=new_panel_embed)

class EditEmbedModal(Modal, title="Edit Embed Modal"):
    def __init__(self):
        super().__init__(timeout=None)
    
        self.embed_title = TextInput(
            label="Title",
            placeholder="Type a title for the embed",
            style=TextStyle.short,
            required=True
        )

        self.embed_description = TextInput(
            label="Description",
            placeholder="Type embed description",
            style=TextStyle.long,
            required=True
        )

        self.embed_color = TextInput(
            label="Color",
            placeholder="Embed color, hex input only #FFFFFF",
            style=TextStyle.short,
            min_length=7,
            max_length=7,
            required=True
        )

        self.add_item(self.embed_title)
        self.add_item(self.embed_description)
        self.add_item(self.embed_color)

    async def on_submit(self, interaction: discord.Interaction):
        if not isValidHexCode(self.embed_color.value):
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Invalid HEX Code!** Please enter a valid hex code.", color=discord.Color.red()), ephemeral=True)
            return
        
        msg_embed = interaction.message.embeds[0]

        msg_embed.title = self.embed_title.value
        msg_embed.description = self.embed_description.value
        msg_embed.color = hex_to_int(self.embed_color.value[1:])

        await interaction.response.edit_message(embed=msg_embed)