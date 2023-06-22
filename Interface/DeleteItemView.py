import sqlite3
import discord

from discord import ButtonStyle, TextStyle
from discord.ui import Modal, TextInput, Select, RoleSelect, View, Button, button, select

database = sqlite3.connect("./Databases/shop.sqlite")

class DeleteItemSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ItemSelector())

class ItemSelector(Select):
    def __init__(self):
        data = database.execute("SELECT id, name, price, available FROM Items").fetchall()
        options = []
        for item in data:
            options.append(discord.SelectOption(label=item[1], description="Price: {} | {}".format(item[2], 'Available' if item[3] == 'yes' else 'Not Available'), value=item[0]))

        super().__init__(placeholder='Select an item to delete...', min_values=1, max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT name, price, available, role FROM Items WHERE id = ?", (self.values[0],)).fetchone()
        role = interaction.guild.get_role(data[3])
        item_embed = discord.Embed(
            title="Editing Item",
            color=discord.Color.blue()
        )
        item_embed.add_field(name="Name:", value=data[0], inline=False)
        item_embed.add_field(name="Price:", value=data[1], inline=False)
        item_embed.add_field(name="Availability:", value="Available" if data[2] == 'yes' else 'Not Available', inline=False)
        item_embed.add_field(name="Role:", value=role.mention, inline=False)

        await interaction.response.edit_message(embed=item_embed, view=ItemDelete(code=self.values[0]))

class ItemDelete(View):
    def __init__(self, code: str):
        self.item_id = code
        super().__init__(timeout=None)
    
    @button(label="Delete", style=ButtonStyle.red)
    async def item_delete_button(self, interaction: discord.Interaction, button: Button):
        database.execute("DELETE FROM Items WHERE id = ?", (self.item_id,)).connection.commit()
        data = database.execute("SELECT * FROM Items").fetchone()
        if data is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ There aren't any items available to delete!", color=discord.Color.red()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Please select an item to delete.", color=discord.Color.blue()), view=DeleteItemSelectorView(), ephemeral=True)