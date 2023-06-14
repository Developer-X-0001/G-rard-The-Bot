import config
import sqlite3
import discord
from discord.ext import commands

class OnMesage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/activity.sqlite")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        config_data = self.database.execute(
            '''
                SELECT
                messagepoints,
                rolepoints,
                role_id,
                channelpoints,
                channel_id,
                rolepointsinchannel,
                role_channel_id,
                channelpointswithrole,
                channel_role_id
                FROM ActivityConfig
                WHERE guild_id = ?
            ''',
            (
                message.guild.id,
            )
        ).fetchone()
        

        guild = message.guild
        user = message.author

        message_points = 1 if config_data is None else config_data[0]
        role_points = 0 if config_data is None else config_data[1]
        role = None if config_data is None else guild.get_role(config_data[2])
        channel_points = 0 if config_data is None else config_data[3]
        channel = None if config_data is None else guild.get_channel(config_data[4])
        roles_points_in_channel = 0 if config_data is None else config_data[5]
        role_for_points_in_channel = None if config_data is None else guild.get_role(config_data[6])
        channel_points_with_role = 0 if config_data is None else config_data[7]
        channel_for_points_with_role = None if config_data is None else guild.get_channel(config_data[8])

        total_points = 1

        total_points *= message_points

        if role in user.roles:
            total_points += role_points

        if role_for_points_in_channel in user.roles and message.channel == channel_for_points_with_role:
            total_points += roles_points_in_channel
            total_points += channel_points_with_role

        if message.channel == channel:
            total_points += channel_points        

        self.database.execute(
            '''
                INSERT INTO UserProfiles VALUES (
                    ?,
                    ?,
                    ?,
                    1,
                    ?,
                    0,
                    0,
                    0
                ) ON CONFLICT (user_id)
                DO UPDATE SET
                    current_points = current_points + ?,
                    total_points = total_points + ?,
                    total_messages = total_messages + 1,
                    message_points = message_points + ?
                    WHERE user_id = ?
            ''',
            (
                user.id,
                total_points,
                total_points,
                total_points,
                total_points,
                total_points,
                total_points,
                user.id,
            )
        ).connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMesage(bot))