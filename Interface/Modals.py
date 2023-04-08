import sqlite3
import discord
from discord import TextStyle
from discord.ui import Modal, TextInput
from Functions.ColorConverter import hex_to_int, int_to_hex

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class EditTitleModal(Modal, title="Edit Embed Title"):
    def __init__(self, old_content: str):
        super().__init__(timeout=None)
        self.input = TextInput(
                        label="New Title",
                        style=TextStyle.short,
                        placeholder="Type a title for the embed...",
                        default=old_content,
                        required=True
                    )
        
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.title = str(self.input.value)
        await interaction.response.edit_message(embed=embed)

class EditDescModal(Modal, title="Edit Embed Description"):
    def __init__(self, old_content: str):
        super().__init__(timeout=None)
        self.input = TextInput(
                        label="New Description",
                        style=TextStyle.long,
                        placeholder="Type a description for the embed...",
                        default=old_content,
                        required=True
                    )
        
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.description = str(self.input.value)
        await interaction.response.edit_message(embed=embed)
    
class EditColorModal(Modal, title="Edit Embed Color"):
    def __init__(self, old_content: str):
        super().__init__(timeout=None)
        self.input = TextInput(
                        label="New Color",
                        style=TextStyle.short,
                        placeholder="Type HEX Color code only! e.g #fff000",
                        default=old_content,
                        min_length=7,
                        max_length=7,
                        required=True
                    )

        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        if not str(self.input).startswith('#'):
            await interaction.response.send_message(embed=discord.Embed(description="InvalidArgument, Please use this format `#FFF000` to change color.", color=discord.Color.red()), ephemeral=True)
            return
        
        embed = interaction.message.embeds[0]
        embed.color = hex_to_int(str(self.input)[1:])
        await interaction.response.edit_message(embed=embed)

class AddChoiceModal(Modal, title="Add New Choice"):
    def __init__(self, view, panel_id: str):
        self.view = view
        self.panel_id = panel_id
        super().__init__(timeout=None)

    choice_name = TextInput(
        label='Name',
        style=TextStyle.short,
        placeholder='Enter choice name',
        required=True
    )

    choice_role = TextInput(
        label='Role ID',
        style=TextStyle.short,
        placeholder='Enter ID of the target Role',
        required=True
    )

    choice_emoji = TextInput(
        label='Emoji',
        style=TextStyle.short,
        placeholder='Enter UNICODE Emoji Only!! e.g 🌐, 🎉',
        required=False
    )

    choice_description = TextInput(
        label='Description',
        style=TextStyle.short,
        placeholder='Add role description',
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = database.execute(f"SELECT role_id FROM '{self.panel_id}' WHERE role_id = ?", (int(str(self.choice_role)),)).fetchone()
        if data is None:
            database.execute(f"INSERT INTO '{self.panel_id}' VALUES (?, ?, ?, ?)", (str(self.choice_name), int(str(self.choice_role)), str(self.choice_emoji), str(self.choice_description),)).connection.commit()
            await interaction.response.send_message(embed=discord.Embed(description="Success, New choice created.", color=discord.Color.green()), ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self.view)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="UniqueConstraintFailed, The selected role is already assigned.", color=discord.Color.red()), ephemeral=True)
