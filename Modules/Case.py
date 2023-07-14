import config
import string
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands
from Interface.CasesConfig import CasesConfigView
from Interface.CaseView import CaseView

class Case(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")
        self.settings_database = sqlite3.connect("./Databases/settings.sqlite")
    
    case_group = app_commands.Group(name="cases", description="Commands related to managing cases module.")

    @case_group.command(name="config", description="Configure cases module.")
    async def cases_config(self, interaction: discord.Interaction):
        config_embed = discord.Embed(
            title="Cases System Configuration",
            color=discord.Color.blue()
        )
        config_embed.add_field(
            name="Cases Channel:",
            value="Not configured yet.",
            inline=True
        )
        config_embed.add_field(
            name="Cases Logs Channel:",
            value="Not configured yet.",
            inline=True
        )
        config_embed.add_field(
            name="Cases Ping Role:",
            value="Not configured yet.",
            inline=True
        )

        await interaction.response.send_message(embed=config_embed, view=CasesConfigView(), ephemeral=True)
    
    @app_commands.command(name="case", description="Open a case against the mentioned user.")
    @app_commands.describe(
        user="User whos against this case is being opened",
        reason="Reason for opening case"   
    )
    async def _case(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
        data = self.settings_database.execute("SELECT cases_channel, cases_log_channel, cases_role FROM CasesModuleSettings WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data is None:
            await interaction.response.send_message(embed=discord.Embed(description="⚠ Cases module isn't configured yet. Run command </cases config:1129509374298173460> to configure it.", color=discord.Color.orange()), ephemeral=True)
            return
        
        else:
            case_channel = interaction.guild.get_channel(data[0])
            case_logs_channel = interaction.guild.get_channel(data[1])
            case_role = interaction.guild.get_role(data[2])
            opened_at = round(datetime.datetime.now().timestamp())

            case_embed = discord.Embed(
                title=f"Case {id}",
                description=f"**Suspect:** {user.mention}\n"
                            f"**Moderator:** {interaction.user.mention}\n"
                            f"**Reason:** {reason}\n\n"
                            f"**Status:** Open\n"
                            f"**Opened At:** <t:{opened_at}:f>\n"
                            f"**Closed At:** N/A\n",
                color=discord.Color.yellow()
            )

            case_msg = await case_channel.send(content=case_role.mention, embed=case_embed, view=CaseView())
            case_thread = await case_msg.create_thread(name=f"Case {id} Discussion")

        self.database.execute(
            "INSERT INTO Cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)",
            (
                id,
                user.id,
                interaction.user.id,
                reason,
                case_thread.id,
                case_msg.id,
                'open',
                opened_at
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description=f"✅ [Case {id}]({case_msg.jump_url}) has been opened against **{user.mention}**.", color=discord.Color.green()), ephemeral=True)
        self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, interaction.user.id, 'case', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
        await case_logs_channel.send(embed=discord.Embed(title="Case Log", description=f"**Target:** {user.mention}\n**Moderator: {interaction.user.mention}**\n**Reason:** {reason}", color=discord.Color.blue()))


async def setup(bot: commands.Bot):
    await bot.add_cog(Case(bot)) 