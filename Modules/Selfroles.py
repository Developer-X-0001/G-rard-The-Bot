import random
import string
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from Interface.SelfrolesCreate import CreateSelfRoles
from Interface.SelfrolesEdit import GetPanelSelectorEdit
from Interface.SelfrolesSend import GetPanelSelectorSend
from Interface.SelfrolesDelete import GetPanelSelectorDelete

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class Selfroles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    selfroles = app_commands.Group(name="selfroles", description="Commands related to selfroles/reaction roles")

    @selfroles.command(name="create", description="Create a new reaction role panel")
    async def createReactionRoles(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Creating a new reaction roles panel",
            description="You can customize this embed through the buttons below",
            color=0x000000
        )
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
        embed.set_footer(text=f"ID: {id}")

        await interaction.response.send_message(embed=embed, view=CreateSelfRoles(id), ephemeral=True)

        database.execute(f'''
            CREATE TABLE IF NOT EXISTS '{id}' (
                name TEXT,
                role_id INTEGER,
                emoji TEXT,
                description TEXT,
                PRIMARY KEY (role_id)
            )
        ''')

        database.execute(f"INSERT INTO ReactionRoles VALUES ('{id}', 1, NULL, NULL, NULL)").connection.commit()
    
    @selfroles.command(name="delete", description="Delete a reaction role panel")
    async def deleteReactionRoles(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchone()
        if data is not None:
            embed = discord.Embed(
                title="Deleting a reaction roles panel",
                description="Please select which panel you want to delete.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, view=GetPanelSelectorDelete(), ephemeral=True)
        else:
            embed = discord.Embed(
                description="There are no reaction roles panel available!",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @selfroles.command(name="edit", description="Edit a reaction role panel")
    async def editReactionRoles(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchone()
        if data is not None:
            embed = discord.Embed(
                title="Editing a reaction roles panel",
                description="Please select a panel you want to delete.",
                color=discord.Color.yellow()
            )

            await interaction.response.send_message(embed=embed, view=GetPanelSelectorEdit(), ephemeral=True)
        else:
            embed = discord.Embed(
                description="There are no reaction roles panel available!",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @selfroles.command(name="send", description="Send a reaction role panel")
    async def sendReactionRoles(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT panel_id, message_id, channel_id FROM ReactionRoles").fetchone()
        if data is not None:
            embed = discord.Embed(
                title="Sending a reaction roles panel",
                description="Please select a panel you want to send again.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Note: The previous panel will be deleted if found any")

            await interaction.response.send_message(embed=embed, view=GetPanelSelectorSend(), ephemeral=True)
        else:
            embed = discord.Embed(
                description="There are no reaction roles panel available!",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Selfroles(bot))