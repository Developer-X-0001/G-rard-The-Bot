import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/moderation.sqlite")

class MemberInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Shows information about the user")
    @app_commands.describe(user="User who's information you want to get.")
    @app_commands.choices(hidden=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    @app_commands.describe(
        user="User whos information you want to see",
        hidden="Either the information comes hidden or visible to all"
    )
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member, hidden: app_commands.Choice[int]=None):
        if hidden is not None and hidden.value == 1:
            ephemeral = True
        elif hidden is not None and hidden.value == 0:
            ephemeral = False
        elif hidden is None:
            ephemeral = True

        report_data = database.execute("SELECT * FROM Modlogs WHERE user_id = ? AND action = ?", (user.id, 'report')).fetchall()
        if report_data == []:
            reports = 0
        else:
            reports = len(report_data)

        warn_data = database.execute("SELECT * FROM Modlogs WHERE user_id = ? AND action = ?", (user.id, 'warn')).fetchall()
        if warn_data == []:
            warns = 0
        else:
            warns = len(warn_data)
        
        timeout_data = database.execute("SELECT * FROM Modlogs WHERE user_id = ? AND action = ?", (user.id, 'timeout')).fetchall()
        if timeout_data == []:
            timeouts = 0
        else:
            timeouts = len(timeout_data)
        
        ban_data = database.execute("SELECT * FROM Modlogs WHERE user_id = ? AND action = ?", (user.id, 'ban')).fetchall()
        if ban_data == []:
            bans = 0
        else:
            bans = len(ban_data)
        
        case_data = database.execute("SELECT * FROM Modlogs WHERE user_id = ? AND action = ?", (user.id, 'case')).fetchall()
        if case_data == []:
            cases = 0
        else:
            cases = len(case_data)

        roles = user.roles
        roles.pop(0)
        
        roles = "\n"
        all_roles = user.roles
        all_roles.reverse()
        for role in all_roles:
            if role.name == "@everyone":
                pass
            else:
                roles += f"{role.mention}, "

        embed = discord.Embed(
            title=f"{user.name}'s Information",
            description=f"**Username:** {user.name}\n"
                        f"**Mention (ID):** {user.mention} ({user.id})\n"
                        f"**Account Created On:** <t:{round(user.created_at.timestamp())}:D>\n"
                        f"**Date Joined Server:** <t:{round(user.joined_at.timestamp())}:d>\n"
                        f"**Roles:** {roles[:-2]}\n\n"
                        f"**Reports:** {reports}\n"
                        f"**Warns:** {warns}\n"
                        f"**Timeouts:** {timeouts}\n"
                        f"**Bans:** {bans}\n"
                        f"**Cases:** {cases}",
            color=user.color
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberInfo(bot))