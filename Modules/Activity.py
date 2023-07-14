import config
import sqlite3
import discord
import datetime
from discord.ext import commands
from discord import app_commands

class Activity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/activity.sqlite")
    
    activity_group = app_commands.Group(name="activities", description="Commands related to activity system.")

    @app_commands.command(name="activity", description="Shows every information about someone's participation.")
    @app_commands.describe(
        user="Member who's activity information you want to see."
    )
    async def _activity(self, interaction: discord.Interaction, user: discord.Member=None):
        if user is None:
            user = interaction.user

        data = self.database.execute("SELECT current_points, total_points, total_messages, message_points, total_invites, invite_points, items_shopped FROM UserProfiles WHERE user_id = ?", (interaction.user.id,)).fetchone()

        current_points = 0 if data is None else data[0]
        total_points = 0 if data is None else data[1]
        total_messages = 0 if data is None else data[2]
        message_points = 0 if data is None else data[3]
        total_invites = 0 if data is None else data[4]
        invite_points = 0 if data is None else data[5]
        items_shopped = 0 if data is None else data[6]

        activity_embed = discord.Embed(
            title=f"{user.name}'s Activity Data",
            description="Showing data since I've started operating in this server.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        activity_embed.add_field(
            name="Data:",
            value=f'''
                Total Points (Ever): {total_points}
                Total Points (Current): {current_points}
                Message Points: {message_points}
                Total Messages: {total_messages}
                Invite Points: {invite_points}
                Total Invites: {total_invites}
                Items Shopped: {items_shopped}
            '''
        )

        await interaction.response.send_message(embed=activity_embed)

    @activity_group.command(name="set-message-points", description="Set how many points are given per message.")
    @app_commands.describe(
        amount="Amount of points."
    )
    async def set_message_points(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO ActivityConfig VALUES (
                    ?,
                    1,
                    ?,
                    0,
                    NULL,
                    0,
                    NULL,
                    0,
                    NULL,
                    NULL
                ) ON CONFLICT (guild_id)
                DO UPDATE SET 
                    messagepoints = ?
                    WHERE guild_id = ?
            ''',
            (
                interaction.guild.id,
                amount,
                amount,
                interaction.guild.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Points given per message has been set to `{}`!".format(amount), color=discord.Color.green()), ephemeral=True)

    @activity_group.command(name="set-channel-points", description="Set how many points are given when a message is sent in a specific channel.")
    @app_commands.describe(
        channel="Channel in which points are given when messaged.",
        amount="Amount of points."
    )
    async def set_channel_points(self, interaction: discord.Interaction, channel: discord.TextChannel, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO ActivityConfig VALUES (
                    ?,
                    1,
                    1,
                    0,
                    NULL,
                    ?,
                    ?,
                    0,
                    NULL,
                    NULL
                ) ON CONFLICT (guild_id)
                DO UPDATE SET 
                    channelpoints = ?,
                    channel_id = ?
                    WHERE guild_id = ?
            ''',
            (
                interaction.guild.id,
                amount,
                channel.id,
                amount,
                channel.id,
                interaction.guild.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Points given per message sent in {} has been set to `{}`!".format(channel.mention, amount), color=discord.Color.green()), ephemeral=True)

    @activity_group.command(name="set-role-points", description="Set how many points are given when someone sends a message having specifc role.")
    @app_commands.describe(
        role="Role when having points are given.",
        amount="Amount of points."
    )
    async def set_role_points(self, interaction: discord.Interaction, role: discord.Role, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO ActivityConfig VALUES (
                    ?,
                    1,
                    1,
                    ?,
                    ?,
                    0,
                    NULL,
                    0,
                    NULL,
                    NULL
                ) ON CONFLICT (guild_id)
                DO UPDATE SET 
                    rolepoints = ?,
                    role_id = ?
                    WHERE guild_id = ?
            ''',
            (
                interaction.guild.id,
                amount,
                role.id,
                amount,
                role.id,
                interaction.guild.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Points given per message sent when having {} role has been set to `{}`!".format(role.mention, amount)), ephemeral=True)

    @activity_group.command(name="set-role-and-channel-points", description="Set how many points to give if user has a role and message in specific channel.")
    @app_commands.describe(
        role="Role when having points are given.",
        channel="Channel in which points are given when messaged.",
        amount="Amount of points."
    )
    async def set_role_and_channel_points(self, interaction: discord.Interaction, role: discord.Role, channel: discord.TextChannel, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO ActivityConfig VALUES (
                    ?,
                    1,
                    1,
                    0,
                    NULL,
                    0,
                    NULL,
                    ?,
                    ?,
                    ?
                ) ON CONFLICT (guild_id)
                DO UPDATE SET 
                    roleandchannelpoints = ?,
                    role_channel_id = ?,
                    channel_role_id = ?
                    WHERE guild_id = ?
            ''',
            (
                interaction.guild.id,
                amount,
                role.id,
                channel.id,
                amount,
                role.id,
                channel.id,
                interaction.guild.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Points given per message sent in {} when having {} role has been set to `{}`!".format(channel.mention, role.mention, amount), color=discord.Color.green()), ephemeral=True)

    @activity_group.command(name="set-invite-points", description="Set how many points are given per invite.")
    @app_commands.describe(
        amount="Amount of points."
    )
    async def set_invite_points(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO ActivityConfig VALUES (
                    ?,
                    ?,
                    1,
                    0,
                    NULL,
                    0,
                    NULL,
                    0,
                    NULL,
                    NULL
                ) ON CONFLICT (guild_id)
                DO UPDATE SET 
                    invitepoints = ?
                    WHERE guild_id = ?
            ''',
            (
                interaction.guild.id,
                amount,
                amount,
                interaction.guild.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Points given per invite has been set to `{}`!".format(amount), color=discord.Color.green()), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Activity(bot))