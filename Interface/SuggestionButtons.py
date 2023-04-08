import sqlite3
import discord
from discord import ButtonStyle
from discord.ui import View, button, Button

database = sqlite3.connect("./Databases/suggestions.sqlite")

class SuggestionButtonsView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(emoji='⏫', style=ButtonStyle.blurple, custom_id="suggestion_upvote")
    async def suggestionUpvote(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT suggestion_id FROM Suggestions WHERE message_id = ?", (interaction.message.id,)).fetchone()
        upvotes_data = database.execute(f"SELECT upvotes FROM '{data[0]}' WHERE upvotes = ?", (interaction.user.id,)).fetchone()
        downvotes_data = database.execute(f"SELECT downvotes FROM '{data[0]}' WHERE downvotes = ?", (interaction.user.id,)).fetchone()
        
        if upvotes_data is None and downvotes_data is None:
            database.execute(f"INSERT INTO '{data[0]}' VALUES (?, NULL)", (interaction.user.id,)).connection.commit()
            total_upvotes = database.execute(f"SELECT upvotes FROM '{data[0]}'").fetchall()
            total_downvotes = database.execute(f"SELECT downvotes FROM '{data[0]}'").fetchall()
            upvotes = 0
            for upvote in total_upvotes:
                if upvote[0] is not None:
                    upvotes += 1
            
            downvotes = 0
            for downvote in total_downvotes:
                if downvote[0] is not None:
                    downvotes += 1

            embed = interaction.message.embeds[0]
            embed.set_field_at(index=2, name=embed.fields[2].name, value=f"⏫ **{upvotes}**\n⏬ **{downvotes}**")
            await interaction.response.send_message(content="Upvote registered", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed)
            return

        if downvotes_data is not None and upvotes_data is None:
            database.execute(f"DELETE FROM '{data[0]}' WHERE downvotes = ?", (interaction.user.id,)).connection.commit()
            database.execute(f"INSERT INTO '{data[0]}' VALUES (?, NULL)", (interaction.user.id,)).connection.commit()
            total_upvotes = database.execute(f"SELECT upvotes FROM '{data[0]}'").fetchall()
            total_downvotes = database.execute(f"SELECT downvotes FROM '{data[0]}'").fetchall()
            upvotes = 0
            for upvote in total_upvotes:
                if upvote[0] is not None:
                    upvotes += 1
            
            downvotes = 0
            for downvote in total_downvotes:
                if downvote[0] is not None:
                    downvotes += 1

            embed = interaction.message.embeds[0]
            embed.set_field_at(index=2, name=embed.fields[2].name, value=f"⏫ **{upvotes}**\n⏬ **{downvotes}**")
            await interaction.response.send_message(content="Vote switched to Upvote", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed)
            return

        else:
            await interaction.response.send_message(content="Upvote already registered!", ephemeral=True)
            return

    @button(emoji='⏬', style=ButtonStyle.blurple, custom_id="suggestion_downvote")
    async def suggestionDownvote(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT suggestion_id FROM Suggestions WHERE message_id = ?", (interaction.message.id,)).fetchone()
        upvotes_data = database.execute(f"SELECT upvotes FROM '{data[0]}' WHERE upvotes = ?", (interaction.user.id,)).fetchone()
        downvotes_data = database.execute(f"SELECT downvotes FROM '{data[0]}' WHERE downvotes = ?", (interaction.user.id,)).fetchone()
        if upvotes_data is None and downvotes_data is None:
            database.execute(f"INSERT INTO '{data[0]}' VALUES (?, NULL)", (interaction.user.id,)).connection.commit()
            total_upvotes = database.execute(f"SELECT upvotes FROM '{data[0]}'").fetchall()
            total_downvotes = database.execute(f"SELECT downvotes FROM '{data[0]}'").fetchall()
            upvotes = 0
            for upvote in total_upvotes:
                if upvote[0] is not None:
                    upvotes += 1
            
            downvotes = 0
            for downvote in total_downvotes:
                if downvote[0] is not None:
                    downvotes += 1

            embed = interaction.message.embeds[0]
            embed.set_field_at(index=2, name=embed.fields[2].name, value=f"⏫ **{upvotes}**\n⏬ **{downvotes}**")
            await interaction.response.send_message(content="Downvote registered", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed)
            return
        
        if upvotes_data is not None and downvotes_data is None:
            database.execute(f"DELETE FROM '{data[0]}' WHERE upvotes = ?", (interaction.user.id,)).connection.commit()
            database.execute(f"INSERT INTO '{data[0]}' VALUES (NULL, ?)", (interaction.user.id,)).connection.commit()
            total_upvotes = database.execute(f"SELECT upvotes FROM '{data[0]}'").fetchall()
            total_downvotes = database.execute(f"SELECT downvotes FROM '{data[0]}'").fetchall()
            upvotes = 0
            for upvote in total_upvotes:
                if upvote[0] is not None:
                    upvotes += 1
            
            downvotes = 0
            for downvote in total_downvotes:
                if downvote[0] is not None:
                    downvotes += 1

            embed = interaction.message.embeds[0]
            embed.set_field_at(index=2, name=embed.fields[2].name, value=f"⏫ **{upvotes}**\n⏬ **{downvotes}**")
            await interaction.response.send_message(content="Vote switched to Downvote", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed)
            return
    
        else:
            await interaction.response.send_message(content="Downvote already registered!", ephemeral=True)
            return