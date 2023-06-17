import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

database = sqlite3.connect("./Databases/tickets.sqlite")

class OnChannelDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        data = database.execute("SELECT user_id, channel_id FROM UserTickets WHERE channel_id = ?", (channel.id,)).fetchone()
        if data is None:
            return
        
        database.execute("DELETE FROM UserTickets WHERE channel_id = ?", (channel.id,)).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnChannelDelete(bot))