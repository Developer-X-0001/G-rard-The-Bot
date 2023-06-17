import config
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/data.sqlite")

    @app_commands.command(name="ban", description="Ban a member from the server for a specified duration.")
    async def _ban(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Choice[str], reason: str=None):
        if user == interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **You can't ban yourself!**", color=discord.Color.red()), ephemeral=True)
            return

        if reason is None:
            reason = "Not specified"

        duration = 0
        expiry = round(datetime.datetime.now().timestamp()) + duration

        self.database.execute(
            '''
                INSERT INTO Bans VALUES (
                    ?,
                    ?,
                    ?,
                    ?
                ) ON CONFLICT (user_id)
                DO UPDATE SET
                    banned_at = ?,
                    expires_in = ?,
                    reason = ?
                    WHERE user_id = ?
            ''',
            (
                user.id,
                round(datetime.datetime.now().timestamp()),
                duration,
                reason,
                round(datetime.datetime.now().timestamp()),
                duration,
                reason,
                user.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ **{}** has been banned from the server.\n**Ban Expiring in:** <t:{}:f>\n**Reason:** {}".format(user.name, expiry, reason), color=discord.Color.green()), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))