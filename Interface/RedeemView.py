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
        data = database.execute("SELECT name, price, role, image_link FROM Items WHERE id = ?", (self.item_id,)).fetchone()
        user_data = user_database.execute("SELECT current_points FROM UserProfiles WHERE user_id = ?", (interaction.user.id,)).fetchone()
        role = interaction.guild.get_role(data[2])
        item_price = int(data[1])
        user_points = int(user_data[0])
        if user_points < item_price:
            await interaction.response.send_message(embed=discord.Embed(description="❌ Insufficient amount of points!", color=discord.Color.red()), ephemeral=True)
            return

        if user_points >= item_price:
            if role in interaction.user.roles:  
                redeem_settings = database.execute("SELECT redeem_channel, redeem_role FROM RedeemSettings WHERE guild_id = ?", (interaction.guild.id,)).fetchone()
                if redeem_settings is None:
                    await interaction.response.send_message(embed=discord.Embed(description="⚠ Redeem settings aren't configured yet!", color=discord.Color.yellow()), ephemeral=True)
                    return
                
                await interaction.response.defer()
                redeem_manager_role = interaction.guild.get_role(redeem_settings[1])
                redeem_logs_channel = interaction.guild.get_channel(redeem_settings[0])

                redeem_embed = discord.Embed(
                    title="Item Redeem Request",
                    color=discord.Color.blue()
                )
                redeem_embed.add_field(
                    name="__Item Name:__",
                    value=data[0],
                    inline=False
                )
                redeem_embed.add_field(
                    name="__Item Details:__",
                    value="**Item ID:** {}\n**Price:** {}\n**Required Role:** {}".format(self.item_id, data[1], role.mention),
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
                redeem_embed.set_thumbnail(url=data[3])

                redeem_msg = await redeem_logs_channel.send(content="{} {}".format(redeem_manager_role.mention, interaction.user.mention), embed=redeem_embed, view=RedeemRequestView())
                redeem_thread = await redeem_msg.create_thread(name="Purchase {}".format(self.item_id))
                user_database.execute("UPDATE UserProfiles SET current_points = current_points - ? WHERE user_id = ?", (item_price, interaction.user.id,)).connection.commit()
                database.execute(
                    '''
                        INSERT INTO CurrentRedeems VALUES (?, ?, ?, ?, NULL, ?)
                    ''',
                    (
                        redeem_msg.id,
                        self.item_id,
                        redeem_thread.id,
                        interaction.user.id,
                        'pending'
                    )
                ).connection.commit()
                await interaction.edit_original_response(embed=discord.Embed(description="Your [redeem request]({}) has been created.".format(redeem_thread.jump_url), color=discord.Color.blue()), view=None)
        
            else:
                await interaction.response.edit_message(embed=discord.Embed(description="❌ You must have {} role to redeem this item!".format(role.mention), color=discord.Color.red()), view=None)