import sqlite3
import discord
from discord.ext import commands

database = sqlite3.connect("./Databases/tickets.sqlite")

class OnRawMessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        data = database.execute("SELECT channel_id, message_id FROM TicketPanels WHERE message_id = ?", (payload.message_id,)).fetchone()
        if data is None:
            return
        
        database.execute("DELETE FROM TicketPanels WHERE message_id = ?", (payload.message_id,)).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnRawMessageDelete(bot))