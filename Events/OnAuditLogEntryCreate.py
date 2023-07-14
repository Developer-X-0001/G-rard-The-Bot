import config
import string
import random
import sqlite3
import discord
import datetime

from discord.ext import commands

class OnAuditLogEntryCreate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/moderation.sqlite")

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
        if entry.action.name == 'ban':
            target = entry.target
            moderator = entry.user
            reason = entry.reason
            self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, target.id, moderator.id, 'ban', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
        
        if entry.action.name == 'unban':
            target = entry.target
            moderator = entry.user
            reason = entry.reason
            self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, target.id, moderator.id, 'unban', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
            
            data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT ban_log_channel FROM LogChannels WHERE guild_id = ?", (entry.guild.id,)).fetchone()
            if data is None:
                return
            else:
                channel = entry.guild.get_channel(data[0])
                await channel.send(embed=discord.Embed(title="Unban Log", description=f"**Target:** {target.mention}\n**Moderator: {moderator.mention}**\n**Reason:** {reason}", color=discord.Color.blue()))
                return

        if entry.action.name == 'kick':
            target = entry.target
            moderator = entry.user
            reason = entry.reason
            self.database.execute("INSERT INTO ModLogs VALUES (?, ?, ?, ?, ?, ?)", (id, target.id, moderator.id, 'kick', round(datetime.datetime.now().timestamp()), reason,)).connection.commit()
            
            data = sqlite3.connect("./Databases/settings.sqlite").execute("SELECT kick_log_channel FROM LogChannels WHERE guild_id = ?", (entry.guild.id,)).fetchone()
            if data is None:
                return
            else:
                channel = entry.guild.get_channel(data[0])
                await channel.send(embed=discord.Embed(title="Kick Log", description=f"**Target:** {target.mention}\n**Moderator: {moderator.mention}**\n**Reason:** {reason}", color=discord.Color.blue()))
                return
    
async def setup(bot: commands.Bot):
    await bot.add_cog(OnAuditLogEntryCreate(bot))