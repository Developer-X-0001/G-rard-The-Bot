import config
import sqlite3
import discord

from discord.ext import commands

database = sqlite3.connect("./Databases/moderation.sqlite")

class OnMemberUnban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.Member):
        data = database.execute("SELECT user_id FROM Bans WHERE user_id = ?", (user.id,)).fetchone()
        if data:
            database.execute("DELETE FROM Bans WHERE user_id = ?", (user.id,)).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberUnban(bot))