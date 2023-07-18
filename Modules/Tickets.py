import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Interface.TicketsConfig import TicketsConfigView

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

        data = self.database.execute("SELECT ticket_method, manager_role, dm_responses, log_channel FROM TicketsConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data is None:
            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured",
                inline=True
            )
            config_embed.add_field(
                name="Ticket Manager Role",
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
            await interaction.response.send_message(embed=config_embed, view=TicketsConfigView(), ephemeral=True)
            self.database.execute("INSERT INTO TicketsConfig VALUES (?, NULL, NULL, NULL, NULL)", (interaction.guild.id,)).connection.commit()
            
        else:
            config_embed.add_field(
                name="Ticketing Method",
                value="Not Configured" if not data[0] else data[0].capitalize(),
                inline=True
            )
            config_embed.add_field(
                name="Ticket Manager Role",
                value="Not Configured" if not data[1] else interaction.guild.get_role(data[1]).mention,
                inline=True
            )
            config_embed.add_field(
                name="DM Responses",
                value="Not Configured" if not data[2] else data[2].capitalize(),
                inline=True
            )
            config_embed.add_field(
                name="Log Channel",
                value="Not Configured" if not data[3] else interaction.guild.get_channel(data[3]).mention,
                inline=True
            )
            await interaction.response.send_message(embed=config_embed, view=TicketsConfigView(), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))