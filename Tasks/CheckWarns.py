import config
import string
import random
import sqlite3
import datetime

from discord.ext import commands, tasks

database = sqlite3.connect("./Databases/moderation.sqlite")

class CheckWarns(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_warns.start()
    
    @tasks.loop(seconds=1)
    async def check_warns(self):
        await self.bot.wait_until_ready()
        data = database.execute("SELECT user_id, expires_in FROM Warns WHERE type = ?", ('temporary',)).fetchall()
        if data is not None:
            for entry in data:
                if round(datetime.datetime.now().timestamp()) > entry[1]:
                    user = self.bot.get_user(entry[0])
                    database.execute("DELETE FROM Warns WHERE user_id = ? AND expires_in = ?", (user.id, entry[1])).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckWarns(bot))