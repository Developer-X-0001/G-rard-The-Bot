import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Interface.TicketsConfig import TicketsConfigView
from Interface.TicketInformationView import TicketSelectorView

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/tickets.sqlite")
    
    tickets_group = app_commands.Group(name="tickets", description="Commands related to ticketing system.")

    @tickets_group.command(name="config", description="Configure tickets system in your discord server.")
    async def _config(self, interaction: discord.Interaction):
        config_embed = discord.Embed(
            title="Ticket System Configuration",
            color=discord.Color.blue()
        )

        data = self.database.execute("SELECT ticket_method, dm_responses, log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        panels_data = self.database.execute("SELECT panel_id, panel_title, panel_description, panel_emoji, panel_role, panel_category FROM TicketPanels").fetchall()
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
            self.database.execute("INSERT INTO TicketsConfig VALUES (?, NULL, NULL, NULL)", (interaction.guild.id,)).connection.commit()
            
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
            await interaction.response.send_message(embed=config_embed, view=TicketsConfigView(), ephemeral=True)
    
    @app_commands.command(name="my-tickets", description="Shows your ticket history")
    async def my_tickets(self, interaction: discord.Interaction):
        tickets_data = self.database.execute("SELECT panel_id, channel_id, status, timestamp FROM UserTickets WHERE user_id = ? ORDER BY timestamp DESC", (interaction.user.id,)).fetchall()

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
            await interaction.response.send_message(embed=embed, view=TicketSelectorView(user_id=interaction.user.id), ephemeral=True)
            return
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))