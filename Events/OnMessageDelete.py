import sqlite3
import discord
from discord.ext import commands

database = sqlite3.connect("./Databases/suggestions.sqlite")

class OnMessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        try:
            guild = self.bot.get_guild(payload.guild_id)
        except:
            return
        try:
            channel = guild.get_channel(payload.channel_id)
        except:
            return
        try:
            message = channel.get_partial_message(payload.message_id)
        except:
            return

        data = database.execute("SELECT suggestion_id FROM Suggestions WHERE message_id = ?", (message.id,)).fetchone()
        if data is None:
            return
        
        database.execute(f"DROP TABLE '{data[0]}'").connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageDelete(bot))