import config
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import ButtonStyle, TextStyle
from discord.ui import View, Button, Modal, TextInput, button

database = sqlite3.connect("./Databases/moderation.sqlite")
settings_database = sqlite3.connect("./Databases/settings.sqlite")

class CaseView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Close", style=ButtonStyle.red, custom_id="close_case_btn")
    async def close_case_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CaseCloseModal(message=interaction.message, case_view=self))
    
    @button(label="Delete", style=ButtonStyle.gray, custom_id="delete_case_btn")
    async def delete_case_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            description="⚠ Deleting the case will delete the message and the case entry from the database.\n\n**Are you sure about this?**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=(CaseDeleteView(message=interaction.message)), ephemeral=True)

class CaseDeleteView(View):
    def __init__(self, message: discord.Message):
        self.case_message = message
        super().__init__(timeout=None)
    
    @button(label="Yes", style=ButtonStyle.green)
    async def delete_yes_button(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT case_id FROM Cases WHERE message_id = ?", (self.case_message.id,)).fetchone()
        await self.case_message.delete()
        await interaction.response.edit_message(embed=discord.Embed(description=f"✅ Case {data[0]} has been deleted.", color=discord.Color.green()), view=None)
        database.execute("DELETE FROM Cases WHERE message_id = ?", (self.case_message.id,)).connection.commit()

    @button(label="No", style=ButtonStyle.red)
    async def delete_no_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=discord.Embed(description="❌ Prompt cancelled!", color=discord.Color.red()), view=None)
    
class CaseCloseModal(Modal, title="Case Close Modal"):
    def __init__(self, message: discord.Message, case_view: CaseView):
        self.case_message = message
        self.case_view = case_view
        super().__init__(timeout=None)
    
    decision = TextInput(
        label="Decision:",
        placeholder="Write your decision here...",
        style=TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = database.execute("SELECT case_id, user, reason, thread_id, opened_at FROM Cases WHERE message_id = ?", (interaction.message.id,)).fetchone()
        
        case_id = data[0]
        user = interaction.guild.get_member(data[1])
        reason = data[2]
        thread = interaction.channel.get_thread(data[3])
        opened_at = data[4]
        close_at = round(datetime.datetime.now().timestamp())

        case_embed = discord.Embed(
            title=f"Case {case_id}",
            description=f"**Suspect:** {user.mention}\n"
                        f"**Moderator:** {interaction.user.mention}\n"
                        f"**Reason:** {reason}\n\n"
                        f"**Status:** Closed\n"
                        f"**Opened At:** <t:{opened_at}:f>\n"
                        f"**Closed At:** <t:{close_at}:f>\n\n"
                        f"**Decision:** {self.decision.value}",
            color=discord.Color.red()
        )

        self.case_view.close_case_button.disabled = True
        self.case_view.close_case_button.label = "Closed"

        await thread.delete()
        await interaction.response.edit_message(embed=case_embed, view=self.case_view)