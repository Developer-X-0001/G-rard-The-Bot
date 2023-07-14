import config
import string
import random
import sqlite3
import datetime

from discord.ext import commands, tasks

database = sqlite3.connect("./Databases/moderation.sqlite")

class CheckBans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_bans.start()
    
    @tasks.loop(seconds=1)
    async def check_bans(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config.GUILD_ID)
        data = database.execute("SELECT user_id, expires_in FROM Bans WHERE type = ?", ('temporary',)).fetchall()
        if data is not None:
            for entry in data:
                if round(datetime.datetime.now().timestamp()) > entry[1]:
                    try:
                        user = self.bot.get_user(entry[0])
                        await guild.unban(user=user, reason="Ban expired.")
                        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                        database.execute("DELETE FROM Bans WHERE user_id = ? AND expires_in = ?", (user.id, entry[1])).connection.commit()
                        database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, user.id, self.bot.user.id, 'unban', round(datetime.datetime.now().timestamp()), 'Ban expired',)).connection.commit()
                    except:
                        raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckBans(bot))