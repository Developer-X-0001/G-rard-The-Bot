import config
import sqlite3
import discord
import datetime
from discord.ext import commands
from discord.ui import View, button, Button
from discord import app_commands, ButtonStyle

database = sqlite3.connect("./Databases/moderation.sqlite")

import discord
from discord import TextStyle
from discord.ui import Modal, TextInput

class ReportCloseModal(Modal, title="Reason for Closing the Report"):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(timeout=None)

    input = TextInput(
        label="Reason",
        style=TextStyle.long,
        placeholder="Type the reason for closing this report.",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = database.execute("SELECT user_id, reported_user, message_id FROM Reports WHERE thread_id = ?", (self.thread_id,)).fetchone()
        message = await interaction.guild.get_channel(config.REPORT_QUEUE_CHANNEL).fetch_message(int(data[2]))
        user = interaction.guild.get_member(int(data[0]))
        reported_user = interaction.guild.get_member(int(data[1]))
        thread = interaction.guild.get_thread(self.thread_id)

        embed = discord.Embed(
            title="Report Closed",
            description="The user was found to be guilty for their actions.\n"
                        "**__Report Details:__**\n"
                        f"Reported By: {user.mention} ({user.id})\n"
                        f"User Reported: {reported_user.mention} ({reported_user.id})\n"
                        f"Reason: {str(self.input)}\n"
                        f"Report Closed At: <t:{round(datetime.datetime.now().timestamp())}:f>",
            color=discord.Color.red()
        )

        report_logs_channel = interaction.guild.get_channel(config.REPORT_LOG_CHANNEL)
        await message.delete()
        await thread.delete()
        await report_logs_channel.send(embed=embed)
        await interaction.response.defer()
    
class UnReportModal(Modal, title="Reason for Unreporting"):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(timeout=None)

    input = TextInput(
        label="Reason",
        style=TextStyle.long,
        placeholder="Type the reason for unreporting.",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = database.execute("SELECT user_id, reported_user, message_id FROM Reports WHERE thread_id = ?", (self.thread_id,)).fetchone()
        message = await interaction.guild.get_channel(config.REPORT_QUEUE_CHANNEL).fetch_message(int(data[2]))
        user = interaction.guild.get_member(int(data[0]))
        reported_user = interaction.guild.get_member(int(data[1]))
        thread = interaction.guild.get_thread(self.thread_id)

        embed = discord.Embed(
            title="Report Closed",
            description="The user was found to be innocent.\n"
                        "**__Report Details:__**\n"
                        f"Reported By: {user.mention} ({user.id})\n"
                        f"User Reported: {reported_user.mention} ({reported_user.id})\n"
                        f"Reason: {str(self.input)}\n"
                        f"Report Closed At: <t:{round(datetime.datetime.now().timestamp())}:f>",
            color=discord.Color.red()
        )

        report_logs_channel = interaction.guild.get_channel(config.REPORT_LOG_CHANNEL)
        await message.delete()
        await thread.delete()
        await report_logs_channel.send(embed=embed)
        await interaction.response.defer()

class ReportButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close", style=ButtonStyle.red, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ReportCloseModal(interaction.channel.id))
    
    # @button(label="Unreport", style=ButtonStyle.green, custom_id="unreport")
    # async def unreport(self, interaction: discord.Interaction, button: Button):
    #     user_data = database.execute("SELECT reported_user FROM Reports WHERE thread_id = ?", (interaction.channel.id,)).fetchone()
    #     data = database.execute("SELECT reports FROM UserData WHERE user_id = ?", (int(user_data[0])))
    #     reports = int(data[0]) - 1
    #     if reports < 0:
    #         reports = 0
        
    #     database.execute("UPDATE UserData SET reports = ? WHERE user_id = ?", (reports, int(user_data[0]),)).connection.commit()
    #     await interaction.response.send_modal(UnReportModal(interaction.channel.id))

class JoinReport(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Join Report", style=ButtonStyle.red, custom_id="join_report")
    async def joinReport(self, interaction: discord.Interaction, button: Button):
        self.joinReport.disabled = True
        self.joinReport.label = f"Claimed By: {interaction.user.name}"
        await interaction.response.edit_message(view=self)
        data = database.execute("SELECT thread_id FROM Reports WHERE message_id = ?", (interaction.message.id,)).fetchone()
        thread = interaction.guild.get_thread(int(data[0]))
        await thread.add_user(interaction.user)

class ReportUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="report", description="Report a certain user")
    @app_commands.describe(user="User whom you want to report", reason="Reason for report")
    async def report(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        reports_channel = interaction.guild.get_channel(config.REPORT_CHANNEL)
        report_queue_channel = interaction.guild.get_channel(config.REPORT_QUEUE_CHANNEL)

        embed = discord.Embed(
            title=f"{user.name}'s Report",
            description="**__Report Information:__**\n"
                        f"User Reported: {user.mention} ({user.id})\n"
                        f"Reason: {reason}\n"
                        f"Report Channel: {interaction.channel.mention}\n"
                        f"Reported At: <t:{round(datetime.datetime.now().timestamp())}:f>",
            color=discord.Color.blue()
        )

        report_embed = discord.Embed(
            title=f"{user.name}'s Report",
            description="**__Report Information:__**\n"
                        f"Reported By: {interaction.user.mention} ({interaction.user.id})\n"
                        f"User Reported: {user.mention} ({user.id})\n"
                        f"Reason: {reason}\n"
                        f"Report Channel: {interaction.channel.mention}\n"
                        f"Reported At: <t:{round(datetime.datetime.now().timestamp())}:f>",
            color=discord.Color.blue()
        )
        report_embed.set_thumbnail(url=user.display_avatar.url)

        thread = await reports_channel.create_thread(type=discord.ChannelType.private_thread, name=f"Report-{user.name}")
        await thread.send(content=user.mention, embed=embed, view=ReportButtons())
        msg = await report_queue_channel.send(embed=report_embed, view=JoinReport())
        database.execute("INSERT INTO Reports VALUES (?, ?, ?, ?)", (interaction.user.id, user.id, thread.id, msg.id,)).connection.commit()
        await interaction.response.send_message(embed=discord.Embed(description="✅ Report Submitted", color=discord.Color.green()), ephemeral=True)
    
    @app_commands.command(name="add-to-thread", description="Add a moderator to report thread")
    @app_commands.describe(user="User whom you want to add in the thread")
    async def addToThread(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.channel.type == discord.ChannelType.private_thread:
            thread = interaction.guild.get_thread(interaction.channel.id)
            await thread.add_user(user)
            await interaction.response.send_message(content=f"{user.mention} will be joining the thread shortly!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReportUser(bot))