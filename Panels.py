import config
import string
import random
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from Interface.PanelModals import PanelChannelSelect

class CreatePanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/tickets.sqlite")

    ticket_panel = app_commands.Group(name="tickets", description="Commands related to ticketing modules")

    @ticket_panel.command(name="create-panel", description="Create a new ticket panel")
    async def ticektPanelCreate(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Creating a New Ticket Panel",
            description="Please fill out the required information to create a new ticket panel.",
            color=discord.Color.green()
        )
        embed.add_field(name="Embed Message:", value="None", inline=True)
        embed.add_field(name="Channel:", value="None", inline=True)
        embed.add_field(name="Category:", value="None", inline=True)
        embed.add_field(name="Ticket Manager:", value="None", inline=True)
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]).upper()
        self.database.execute(f"INSERT INTO TicketPanels VALUES ('{id}', NULL, NULL, NULL, NULL)")
        self.database.commit()
        await interaction.response.send_message(embed=embed, view=PanelChannelSelect(id), ephemeral=True)

    @ticket_panel.command(name="my-tickets", description="Show your opened tickets.")
    async def myTickets(self, interaction: discord.Interaction):
        user_tickets = self.database.execute(
            "SELECT panel_id, channel_id, status, timestamp FROM UserTickets WHERE user_id = ?", (interaction.user.id,)
        ).fetchall()
        
        if user_tickets is None:
            await interaction.response.send_message(embed=discord.Embed(description=f"❌ You don't have any ticket opened!", color=discord.Color.red()), ephemeral=True)
            return

        open_tickets = ""
        open_count = 0
        for ticket in user_tickets:
            if ticket[2] == 'open':
                open_count += 1
                channel = interaction.guild.get_channel(ticket[1])
                open_tickets += f"**{open_count}.** [**Panel:** {ticket[0]} | <t:{ticket[3]}:f>]({channel.jump_url})"
            
            if open_count >= 10:
                break

        closed_tickets = ""
        closed_count = 0
        for ticket in user_tickets:
            if ticket[2] == 'closed':
                closed_count += 1
                closed_tickets += f"**{closed_count}.** **Panel:** {ticket[0]} | <t:{ticket[3]}:f>"
            
            if closed_count >= 10:
                break

        embed = discord.Embed(
            title="Your Tickets History",
            description="These are the tickets you've opened/closed in the past.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Open Tickets:",
            value=open_tickets if open_count != 0 else "No open tickets found.",
            inline=False
        )
        embed.add_field(
            name="Closed Tickets:",
            value=closed_tickets if closed_count != 0 else "No closed tickets found.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CreatePanel(bot))