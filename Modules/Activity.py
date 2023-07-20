import config
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands
from Interface.ActivityConfig import ActivityConfigView

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

    @activity_group.command(name="config", description="Configure activity system in your discord server.")
    async def activity_config(self, interaction: discord.Interaction):
        data = self.database.execute("SELECT invitepoints, messagepoints, rolepoints, role_id, channelpoints, channel_id, roleandchannelpoints, role_channel_id, channel_role_id FROM ActivityConfig WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        
        if data is None:
            config_embed = discord.Embed(
                title="Ticket System Configuration",
                color=discord.Color.blue()
            )
            config_embed.add_field(
                name="Points Per Invite:",
                value="1",
                inline=False
            )
            config_embed.add_field(
                name="Points Per Message:",
                value="1",
                inline=False
            )
            config_embed.add_field(
                name="Points When Having Role:",
                value=f"Role: Not Set\n"
                        f"Points: 0",
                inline=False
            )
            config_embed.add_field(
                name="Points In Channel:",
                value=f"Channel: Not Set\n"
                        f"Points: 0",
                inline=False
            )

            config_embed.add_field(
                name="Points When Having Role & In Channel:",
                value=f"Role: Not Set\n"
                        f"Channel: Not Set\n"
                        f"Points: 0",
                inline=False
            )

            await interaction.response.send_message(embed=config_embed, view=ActivityConfigView(), ephemeral=True)

        else:
            config_embed = discord.Embed(
                title="Ticket System Configuration",
                color=discord.Color.blue()
            )
            config_embed.add_field(
                name="Points Per Invite:",
                value="1" if not data[0] else data[0],
                inline=False
            )
            config_embed.add_field(
                name="Points Per Message:",
                value="1" if not data[1] else data[1],
                inline=False
            )
            config_embed.add_field(
                name="Points When Having Role:",
                value=f"Role: {'Not Set' if not data[3] else interaction.guild.get_role(data[3]).mention}\n"
                        f"Points: {'0' if not data[2] else data[2]}",
                inline=False
            )
            config_embed.add_field(
                name="Points In Channel:",
                value=f"Channel: {'Not Set' if not data[5] else interaction.guild.get_channel(data[5]).mention}\n"
                        f"Points: {'0' if not data[4] else data[4]}",
                inline=False
            )

            config_embed.add_field(
                name="Points When Having Role & In Channel:",
                value=f"Role: {'Not Set' if not data[7] else interaction.guild.get_role(data[7]).mention}\n"
                        f"Channel: {'Not Set' if not data[8] else interaction.guild.get_channel(data[8]).mention}\n"
                        f"Points: {'0' if not data[6] else data[6]}",
                inline=False
            )

            await interaction.response.send_message(embed=config_embed, view=ActivityConfigView(), ephemeral=True)

    @activity_group.command(name="add-points", description="Give points to a user")
    @app_commands.describe(
        user="The user whom you are giving the points.",
        amount="Amount of points."
    )
    async def add_points(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        self.database.execute(
            '''
                INSERT INTO UserProfiles VALUES (
                    ?,
                    ?,
                    ?,
                    0,
                    0,
                    0,
                    0,
                    0
                ) ON CONFLICT (user_id)
                DO UPDATE SET 
                    current_points = current_points + ?,
                    total_points = total_points + ?
                    WHERE user_id = ?
            ''',
            (
                user.id,
                amount,
                amount,
                amount,
                amount,
                user.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully added `{}` points to {}'s activity points.".format(amount, user.mention), color=discord.Color.green()), ephemeral=True)
    
    @activity_group.command(name="remove-points", description="Remove points from a user")
    @app_commands.describe(
        user="The user whose points you are removing.",
        amount="Amount of points."
    )
    async def add_points(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount must be greater than zero!**", color=discord.Color.red()), ephemeral=True)
            return
        
        data = self.database.execute("SELECT current_points FROM UserProfiles WHERE user_id = ?", (user.id,)).fetchone()
        
        current_points = 0 if data is None else data[0]

        if amount > current_points:
            await interaction.response.send_message(embed=discord.Embed(description="❌ **Amount can't be greater than user's current points!**", color=discord.Color.red()), ephemeral=True)
            return

        self.database.execute(
            '''
                INSERT INTO UserProfiles VALUES (
                    ?,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ) ON CONFLICT (user_id)
                DO UPDATE SET 
                    current_points = current_points - ? 
                    WHERE user_id = ?
            ''',
            (
                user.id,
                amount,
                user.id,
            )
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully removed `{}` points from {}'s activity points.".format(amount, user.mention), color=discord.Color.green()), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Activity(bot))