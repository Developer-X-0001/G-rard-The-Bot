import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/data.sqlite")

class MemberInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Shows information about the user")
    @app_commands.describe(user="User who's information you want to get.")
    @app_commands.choices(hidden=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
    ])
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member, hidden: app_commands.Choice[int]=None):
        if hidden is not None and hidden.value == 1:
            ephemeral = True
        elif hidden is not None and hidden.value == 0:
            ephemeral = False
        elif hidden is None:
            ephemeral = True

        warn_data = database.execute("SELECT user_id, mod_id, reason, time FROM Warns WHERE user_id = ? ORDER BY time DESC", (user.id,)).fetchall()
        if warn_data == []:
            warns = 0
        else:
            warns = len(warn_data)
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
                        f"**Reports:** {0}\n"
                        f"**Warns:** {warns}\n"
                        f"**Timeouts:** {0}\n"
                        f"**Bans:** {0}\n"
                        f"**Cases:** {0}",
            color=user.accent_color
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        if warn_data != []:
            mod_user = interaction.guild.get_member(warn_data[0][1])
            embed.add_field(
                name="**Most Recent Warning:**",
                value=f"**Moderator:** {mod_user.mention}\n"
                    f"**Time:** <t:{warn_data[0][3]}:f>\n"
                    f"**Reason:** {warn_data[0][2]}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberInfo(bot))