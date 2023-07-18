import string
import random
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Functions.ImageUrlChecker import is_image_url
from Interface.EditItemView import EditItemSelectorView
from Interface.DeleteItemView import DeleteItemSelectorView

class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/shop.sqlite")

    shop_group = app_commands.Group(name="shop", description="Commands related to shoping system.")

    @shop_group.command(name="create-item", description="Create an item for the named price, availability and role.")
    @app_commands.choices(available=[
        app_commands.Choice(name="Yes", value='yes'),
        app_commands.Choice(name="No", value='no')
    ])
    async def create_item(self, interaction: discord.Interaction, name: str, price: int, available: app_commands.Choice[str], role: discord.Role, image_link: str=None):
        if image_link is None:
            data = self.database.execute("SELECT name FROM Items WHERE name = ?", (name,)).fetchone()
            if data is None:
                id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                self.database.execute("INSERT INTO Items VALUES (?, ?, ?, ?, ?, ?)", (id, name, price, available.value, image_link, role.id,)).connection.commit()
                await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully created a new item: **`{}`**".format(name), color=discord.Color.green()), ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(description="❌ Item with name **`{}`** already exists!".format(name), color=discord.Color.red()), ephemeral=True)

        else:
            if is_image_url(url=image_link):
                data = self.database.execute("SELECT name FROM Items WHERE name = ?", (name,)).fetchone()
                if data is None:
                    id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)]).upper()
                    self.database.execute("INSERT INTO Items VALUES (?, ?, ?, ?, ?, ?)", (id, name, price, available.value, image_link, role.id,)).connection.commit()
                    await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully created a new item: **`{}`**".format(name), color=discord.Color.green()), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=discord.Embed(description="❌ Item with name **`{}`** already exists!".format(name), color=discord.Color.red()), ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(description="❌ Invalid image link!", color=discord.Color.red()), ephemeral=True)
                return

    @shop_group.command(name="edit-items", description="Edit previously made items.")
    async def edit_item(self, interaction: discord.Interaction):
        data = self.database.execute("SELECT * FROM Items").fetchone()
        if data is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ There aren't any items available to edit!", color=discord.Color.red()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Please select an item to edit it's information.", color=discord.Color.blue()), view=EditItemSelectorView(), ephemeral=True)

    @shop_group.command(name="delete-items", description="Delete previously made items.")
    async def delete_item(self, interaction: discord.Interaction):
        data = self.database.execute("SELECT * FROM Items").fetchone()
        if data is None:
            await interaction.response.send_message(embed=discord.Embed(description="❌ There aren't any items available to delete!", color=discord.Color.red()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Please select an item to delete.", color=discord.Color.blue()), view=DeleteItemSelectorView(), ephemeral=True)

    @shop_group.command(name="set-redeem-role", description="Set a role to be pinged when someone tries to redeem an item.")
    async def set_redeem_role(self, interaction: discord.Interaction, role: discord.Role):
        self.database.execute("INSERT INTO RedeemSettings VALUES (?, NULL, ?) ON CONFLICT (guild_id) DO UPDATE SET redeem_role = ? WHERE guild_id = ?",
                              (interaction.guild.id, role.id, role.id, interaction.guild.id,)
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully set {} role as redeem manager role.".format(role.mention), color=discord.Color.green()), ephemeral=True)

    @shop_group.command(name="set-redeem-logs-channel", description="Set a channel to log every item redeem.")
    async def set_redeem_logs_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.database.execute("INSERT INTO RedeemSettings VALUES (?, ?, NULL) ON CONFLICT (guild_id) DO UPDATE SET redeem_channel = ? WHERE guild_id = ?",
                              (interaction.guild.id, channel.id, channel.id, interaction.guild.id,)
        ).connection.commit()

        await interaction.response.send_message(embed=discord.Embed(description="✅ Successfully set {} channel for logging.".format(channel.mention), color=discord.Color.green()), ephemeral=True)

    @shop_group.command(name="list", description="List all available items.")
    async def shop_list(self, interaction: discord.Interaction):
        items_data = self.database.execute("SELECT name, price, role FROM Items WHERE available = ?", ('yes',)).fetchall()
        if items_data is None or items_data == []:
            await interaction.response.send_message(embed=discord.Embed(description="❌ There aren't any items listed.", color=discord.Color.red()), ephemeral=True)
            return
        
        items = ""
        counter = 1
        for item in items_data:
            role = interaction.guild.get_role(item[2])
            items += f"{counter}. {item[0]} | Price: {item[1]} | Role: {role.mention}\n"

        items_embed = discord.Embed(
            title="Currently listed items",
            description=items,
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=items_embed, ephemeral=True)

    @shop_group.command(name="send-list", description="Send all items in a channel. (Defaults to current channel)")
    async def send_list(self, interaction: discord.Interaction, channel: discord.TextChannel=None):
        if channel is None:
            channel = interaction.channel
        
        data = self.database.execute("SELECT name, price, available, image_link, role FROM Items").fetchall()
        
        embed_list = []

        for entry in data:
            role = interaction.guild.get_role(entry[4])

            item_embed = discord.Embed(
                color=discord.Color.blue()
            )
            item_embed.add_field(name="Name:", value=entry[0], inline=False)
            item_embed.add_field(name="Price:", value=entry[1], inline=False)
            item_embed.add_field(name="Availability:", value="Available" if entry[2] == 'yes' else 'Not Available', inline=False)
            item_embed.add_field(name="Role:", value=role.mention, inline=False)
            item_embed.set_footer(text="You must have the required role to redeem this item!")
            item_embed.set_thumbnail(url=entry[3])

            embed_list.append(item_embed)

            if len(embed_list) == 10:
                await channel.send(embeds=embed_list)
                embed_list.clear()
        
        if len(embed_list) > 0:
            await channel.send(embeds=embed_list)
        
        await interaction.response.send_message(embed=discord.Embed(description="✅ All listed items have been sent to {}.".format(channel.mention), color=discord.Color.green()), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))