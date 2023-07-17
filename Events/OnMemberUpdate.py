import config
import sqlite3
import discord

from discord.ext import commands

class OnMemberUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/settings.sqlite")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        data = self.database.execute("SELECT role_log_channel FROM LogChannels WHERE guild_id = ?", (after.guild.id,)).fetchone()
        if data:
            role_log_channel = after.guild.get_channel(data[0])
            if len(before.roles) > len(after.roles):
                lost_roles = set(before.roles) - set(after.roles)
                roles = ""
                for role in lost_roles:
                    roles += "{}\n".format(role.mention)

                log_embed = discord.Embed(
                    title="Role Update Log",
                    description="{} has dropped the following role(s):\n\n{}".format(before.mention, roles),
                    color=discord.Color.blue()
                )

                await role_log_channel.send(embed=log_embed)

            elif len(before.roles) < len(after.roles):
                gained_roles = set(after.roles) - set(before.roles)
                roles = ""
                for role in gained_roles:
                    roles += "{}\n".format(role.mention)

                log_embed = discord.Embed(
                    title="Role Update Log",
                    description="{} has gained the following role(s):\n\n{}".format(before.mention, roles),
                    color=discord.Color.blue()
                )

                await role_log_channel.send(embed=log_embed)
                

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberUpdate(bot))