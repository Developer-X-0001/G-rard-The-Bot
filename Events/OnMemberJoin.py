import sqlite3
import discord
import DiscordUtils

from discord.ext import commands

class OnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)
        self.database = sqlite3.connect("./Databases/activity.sqlite")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        
        inviter = await self.tracker.fetch_inviter(member=member)
        print(inviter)
        config_data = self.database.execute("SELECT invitepoints FROM ActivityConfig WHERE guild_id = ?", (member.guild.id,)).fetchone()

        invite_points = 1 if config_data is None else config_data[0]

        self.database.execute(
            '''
                INSERT INTO UserProfiles VALUES (
                    ?,
                    ?,
                    ?,
                    0,
                    0,
                    1,
                    ?,
                    0
                ) ON CONFLICT (user_id)
                DO UPDATE SET
                    current_points = current_points + ?,
                    total_points = total_points + ?,
                    total_invites = total_invites + 1,
                    invite_points = invite_points + ?
                    WHERE user_id = ?
            ''',
            (
                inviter.id,
                invite_points,
                invite_points,
                invite_points,
                invite_points,
                invite_points,
                invite_points,
                inviter.id,
            )
        ).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberJoin(bot))