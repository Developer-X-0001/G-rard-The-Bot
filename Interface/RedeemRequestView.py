import sqlite3
import discord
import datetime

from discord import ButtonStyle
from discord.ui import View, Button, button

database = sqlite3.connect("./Databases/shop.sqlite")
user_database = sqlite3.connect("./Databases/activity.sqlite")

class RedeemRequestView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Mark as Delivered", style=ButtonStyle.green, custom_id="mark_as_delivered")
    async def mark_as_delivered_button(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT item_id, thread_id FROM CurrentRedeems WHERE message_id = ?", (interaction.message.id,)).fetchone()
        item_embed = interaction.message.embeds[0]
        item_id = data[0]
        thread = interaction.message.channel.get_thread(data[1])
        user = interaction.message.mentions[0]
        item_data = database.execute("SELECT name FROM Items WHERE id = ?", (item_id,)).fetchone()
        sqlite3.connect("./Databases/UserData/{}.sqlite".format(user.id)).execute(
            '''
                CREATE TABLE IF NOT EXISTS Inventory (
                    item_id,
                    item_name,
                    item_amount,
                    Primary Key (item_id)
                )
            '''
        ).execute(
            '''
                INSERT INTO Inventory VALUES (?, ?, ?) ON CONFLICT (item_id) DO UPDATE SET
                    item_amount = item_amount + 1
                    WHERE item_id = ?
            ''',
            (
                item_id,
                item_data[0],
                1,
                item_id,
            )
        ).connection.commit()
        database.execute("UPDATE CurrentRedeems SET status = ? WHERE message_id = ?", ('delivered', interaction.message.id,)).connection.commit()

        item_embed.set_field_at(
            index=4,
            name="__Request Status:__",
            value="Delivered",
            inline=False
        )
        item_embed.add_field(
            name="__Delivered At:__",
            value="<t:{}:f>".format(round(datetime.datetime.now().timestamp())),
            inline=False
        )
        item_embed.color = discord.Color.green()
        await interaction.response.edit_message(embed=item_embed, view=None)
        response_embed = discord.Embed(
            title="Item Delivered",
            description="{} your requested item `{}` has been delivered!".format(user.mention, item_data[0]),
            color=discord.Color.green()
        )
        await thread.send(content=user.mention, embed=response_embed)
        await thread.edit(locked=True)

    @button(label="Reject Request", style=ButtonStyle.red, custom_id="reject_request")
    async def reject_request_button(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT item_id, thread_id FROM CurrentRedeems WHERE message_id = ?", (interaction.message.id,)).fetchone()
        item_embed = interaction.message.embeds[0]
        item_id = data[0]
        thread = interaction.message.channel.get_thread(data[1])
        user = interaction.message.mentions[0]
        item_data = database.execute("SELECT price, name FROM Items WHERE id = ?", (item_id,)).fetchone()
        user_database.execute("UPDATE UserProfiles SET current_points = current_points + ? WHERE user_id = ?", (item_data[0], user.id,)).connection.commit()
        database.execute("UPDATE CurrentRedeems SET status = ? WHERE message_id = ?", ('rejected', interaction.message.id,)).connection.commit()

        item_embed.set_field_at(
            index=4,
            name="__Request Status:__",
            value="Rejected",
            inline=False
        )
        item_embed.add_field(
            name="__Rejected At:__",
            value="<t:{}:f>".format(round(datetime.datetime.now().timestamp())),
            inline=False
        )
        item_embed.set_footer(text="User's points have been refunded.")
        item_embed.color = discord.Color.red()
        await interaction.response.edit_message(embed=item_embed, view=None)
        response_embed = discord.Embed(
            title="Request Rejected",
            description="{} your request for item `{}` has been rejected!".format(user.mention, item_data[1]),
            color=discord.Color.red()
        )
        await thread.send(content=user.mention, embed=response_embed)
        await thread.edit(locked=True)

    @button(label="Claim Thread", style=ButtonStyle.gray, custom_id="claim_thread", row=1)
    async def claim_thread_button(self, interaction: discord.Interaction, button: Button):
        redeem_data = database.execute("SELECT thread_id FROM CurrentRedeems WHERE message_id = ?", (interaction.message.id,)).fetchone()
        user = interaction.message.mentions[0]
        item_embed = interaction.message.embeds[0]
        self.claim_thread_button.disabled = True
        self.claim_thread_button.label = "Handled By: {}".format(interaction.user.name)

        item_embed.set_field_at(
            index=4,
            name="__Request Status:__",
            value="Processing",
            inline=False
        )
        item_embed.color = discord.Color.yellow()

        thread = interaction.channel.get_thread(redeem_data[0])
        await thread.add_user(interaction.user)
        await thread.send(content="{}, your request is being handled by {}".format(user.mention, interaction.user.mention))
        database.execute("UPDATE CurrentRedeems SET handler_id = ? WHERE message_id = ?", (interaction.user.id, interaction.message.id,)).connection.commit()
        await interaction.response.edit_message(embed=item_embed, view=self)