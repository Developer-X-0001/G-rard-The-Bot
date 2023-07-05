import config
import sqlite3
import discord
import datetime

from discord.ext import commands, tasks

database = sqlite3.connect("./Databases/polls.sqlite")

class CheckPolls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_timed_polls.start()

    @tasks.loop(seconds=1)
    async def check_timed_polls(self, interaction: discord.Interaction):
        data = database.execute("SELECT id, channel_id, message_id, user_id, time FROM TimedPolls WHERE status = ?", ('open',)).fetchall()
        poll_channel = self.bot.get_guild(config.GUILD_ID).get_channel(data[1])
        poll_message = await poll_channel.fetch_message(data[2])
        current_time = round(datetime.datetime.now().timestamp())
        poll_time = data[3]

        if current_time >= poll_time:
            poll_embed = poll_message.embeds[0]
            poll_embed.color = discord.Color.red()

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckPolls(bot))