import sqlite3
import discord
from discord import ButtonStyle, TextStyle
from discord.ui import View, button, Button, Modal, TextInput

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class NewRoleModal(Modal, title="Adding New Region"):
    def __init__(self):
        super().__init__(timeout=None)

    region_name = TextInput(
        label="Name",
        style=TextStyle.short,
        placeholder="Region name...",
        required=True
    )

    region_role = TextInput(
        label="Role ID",
        style=TextStyle.short,
        placeholder="Role ID of the corresponding region...",
        required=True
    )

    region_emoji = TextInput(
        label="Region Emoji",
        style=TextStyle.short,
        placeholder="UNICODE Emojis Only! e.g (🇬🇧, 🇳🇱, 🇨🇿)",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(str(self.region_name))
        data = database.execute("SELECT role_id FROM RegionRoles WHERE role_id = ?", (str(self.region_role),)).fetchone()
        if data is None:
            database.execute("INSERT INTO RegionRoles VALUES (?, ?, ?)", (str(self.region_name), int(str(self.region_role)), str(self.region_emoji),)).connection.commit()
            await interaction.response.send_message(content="Successfully added new role!", ephemeral=True)
        else:
            await interaction.response.send_message(content="That role already exists!", ephemeral=True)

# --------------------------------- Button Views ---------------------------------

class RegionRolesEditButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Add Role", style=ButtonStyle.green, custom_id="add_role")
    async def addRole(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(NewRoleModal())
    
    @button(label="Edit Role", style=ButtonStyle.green, custom_id="edit_role")
    async def editRole(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Clicked!")
    
    @button(label="Remove Role", style=ButtonStyle.red, custom_id="remove_role")
    async def removeRole(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Clicked!")
