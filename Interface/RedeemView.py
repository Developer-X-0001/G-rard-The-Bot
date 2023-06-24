import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle
from discord.ui import View, Button, button
from Interface.RedeemRequestView import RedeemRequestView

database = sqlite3.connect("./Databases/shop.sqlite")
user_database = sqlite3.connect("./Databases/activity.sqlite")

class RedeemButton(View):
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(timeout=None)

    @button(label="Redeem", style=ButtonStyle.blurple)
    async def redeem_button(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT name, price, role FROM Items WHERE id = ?", (self.item_id,)).fetchone()
        role = interaction.guild.get_role(data[2])

        if role in interaction.user.roles:
            redeem_settings = database.execute("SELECT redeem_channel, redeem_role FROM RedeemSettings WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
            redeem_manager_role = interaction.guild.get_role(redeem_settings[1])
            redeem_logs_channel = interaction.guild.get_channel(redeem_settings[0])

            redeem_embed = discord.Embed(
                title="Item Redeem Request"
            )
            redeem_embed.add_field(
                name="__Item ID:__",
                value=self.item_id,
                inline=False
            )
            redeem_embed.add_field(
                name="__Item Details:__",
                value="**Item Name:** {}\n**Price:** {}\n**Required Role:** {}".format(data[0], data[1], role.mention),
                inline=False
            )
            redeem_embed.add_field(
                name="__Requested By:__",
                value=interaction.user.mention,
                inline=False
            )
            redeem_embed.add_field(
                name="__Requested At:__",
                value="<t:{}:f>".format(round(datetime.datetime.now().timestamp())),
                inline=False
            )
            redeem_embed.add_field(
                name="__Request Status:__",
                value="Pending",
                inline=False
            )

            redeem_msg = await redeem_logs_channel.send(content=redeem_manager_role.mention, embed=redeem_embed, view=RedeemRequestView())
            redeem_thread = await redeem_msg.create_thread(name="Purchase {}".format(self.item_id))
            await interaction.response.edit_message(embed=discord.Embed(description="Your [redeem request]({}) has been created.".format(redeem_thread.jump_url), color=discord.Color.blue()))
        
        else:
            await interaction.response.edit_message(embed=discord.Embed(description="❌ You must have {} role to redeem this item!".format(role.mention), color=discord.Color.red()))