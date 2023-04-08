import string
import random
import sqlite3
import discord
import datetime
from discord.ext import commands
from discord import app_commands
from Interface.SuggestionsQueue import SuggestionsQueueView
from Interface.SuggestionButtons import SuggestionButtonsView
from Interface.SuggestionsConfig import SuggestionSystemConfigurationView

database = sqlite3.connect("./Databases/suggestions.sqlite")

class Suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    suggestions = app_commands.Group(name="suggestions", description="Commands related to suggestions system")

    @suggestions.command(name="config", description="Configure suggestions system in your discord server.")
    async def s_config(self, interaction: discord.Interaction):
        data = database.execute("SELECT suggestions_channel_id, approved_channel_id, declined_channel_id, dm_status, suggestions_queue, thread_status FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data is None:
            channel = 'Not Configured'
            approved_channel = 'Not Configured'
            declined_channel = 'Not Configured'
            dm_status = '✅ Enabled'
            queueing = '❌ Disabled'
            threads = '✅ Enabled'
        
        else:
            channel = interaction.guild.get_channel(data[0])
            approved_channel = interaction.guild.get_channel(data[1])
            declined_channel = interaction.guild.get_channel(data[2])
            dm_status = f"{'✅' if data[3] == 'Enabled' else '❌ Disabled'}"
            queueing = f"{'✅' if data[4] == 'Enabled' else '❌ Disabled'}"
            threads = f"{'✅' if data[5] == 'Enabled' else '❌ Disabled'}"

        embed = discord.Embed(
            title="Suggestions System Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Suggestions Channel", value=channel.mention if channel != 'Not Configured' else channel, inline=True)
        embed.add_field(name="Approved Suggestions Channel", value=approved_channel.mention if approved_channel != 'Not Configured' else approved_channel, inline=True)
        embed.add_field(name="Declined Suggestions Channel", value=declined_channel.mention if declined_channel != 'Not Configured' else declined_channel, inline=True)
        embed.add_field(name="DM Responses", value=dm_status, inline=True)
        embed.add_field(name="Suggestion Queueing", value=queueing, inline=True)
        embed.add_field(name="Suggestion Threads", value=threads, inline=True)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        await interaction.response.send_message(embed=embed, view=SuggestionSystemConfigurationView(), ephemeral=True)
    
    @suggestions.command(name="queue", description="View suggestions queue")
    async def queue(self, interaction: discord.Interaction):
        data = database.execute("SELECT suggestions_queue FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if data is None or data[0] == 'Disabled':
            await interaction.response.send_message(embed=discord.Embed(description="❌ Suggestions Queue isn't enabled in this server!", color=discord.Color.red()), ephemeral=True)
            return

        else:
            queue_data = database.execute("SELECT suggestion_id, user_id, suggestion FROM Queue").fetchall()
            if queue_data == []:
                await interaction.response.send_message(embed=discord.Embed(description="⚠ No suggestions available in queue", color=discord.Color.gold()), ephemeral=True)
                return
            else:
                embed = discord.Embed(
                    title="Suggestions Queue",
                    description="There are `{}` suggestions availabel in queue. Select a suggestion from the dropdown below to approve or decline it.".format(len(queue_data)),
                    color=discord.Color.blue()
                )

                await interaction.response.send_message(embed=embed, view=SuggestionsQueueView(), ephemeral=True)

    @app_commands.command(name="suggest", description="Create a new suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        channel_data = database.execute("SELECT suggestions_channel_id FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
        if channel_data is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Suggestions channel not found!", color=discord.Color.red()), ephemeral=True)
        else:
            suggestions_channel = interaction.guild.get_channel(channel_data[0])
            queue_data = database.execute("SELECT suggestions_queue FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
            if queue_data is None or queue_data[0] is None or queue_data[0] == 'Disabled':
                thread_data = database.execute("SELECT thread_status FROM Config WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
                id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                embed = discord.Embed(
                    timestamp=datetime.datetime.now(),
                    color=discord.Color.gold()
                )
                embed.add_field(name="Submitter", value=interaction.user.mention, inline=False)
                embed.add_field(name="Suggestion", value=suggestion, inline=False)
                embed.add_field(name="Results so far", value="⏫ **0**\n⏬ **0**")
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text=f"User ID: {interaction.user.id} | sID: {id}")
                msg = await suggestions_channel.send(embed=embed, view=SuggestionButtonsView())
                if thread_data is not None and thread_data[0] == 'Enabled':
                    await msg.create_thread(name=f"Thread for suggestion {id}")
                database.execute("INSERT INTO Suggestions VALUES (?, ?, ?, ?, NULL)", (msg.id, id, interaction.user.id, suggestion)).connection.commit()
                database.execute(f"CREATE TABLE IF NOT EXISTS '{id}' (upvotes INTERGER, downvotes INTEGER)")
                await interaction.response.send_message(embed=discord.Embed(description="✅ Thanks for your suggestion!", color=discord.Color.green()), ephemeral=True)
            else:
                id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                database.execute("INSERT INTO Queue VALUES (?, ?, ?)", (id, interaction.user.id, suggestion,)).connection.commit()
                await interaction.response.send_message(embed=discord.Embed(description="⌚ Your suggestion has been sent to the queue for processing.", color=discord.Color.blue()), ephemeral=True)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestions(bot))