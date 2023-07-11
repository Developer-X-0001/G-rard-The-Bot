import config
import sqlite3
import discord
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
                        database.execute("DELETE FROM Bans WHERE user_id = ?", (user.id,)).connection.commit()
                    except:
                        raise Exception

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckBans(bot))