import sqlite3
import discord
from discord import ButtonStyle
from discord.ui import View, button, Button, select, ChannelSelect, Select

database = sqlite3.connect("./Databases/suggestions.sqlite")

class SuggestionSystemChannelConfigurationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Set Suggestions Channel!', min_values=1, max_values=1, row=0)
    async def suggestionsChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        database.execute("INSERT INTO Config VALUES (?, ?, NULL, NULL, NULL, NULL, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET suggestions_channel_id = ? WHERE guild_id = ?", (interaction.guild.id, select.values[0].id, select.values[0].id, interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=0, name=embed.fields[0].name, value=select.values[0].mention, inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemChannelConfigurationView())

    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Set Approved Suggestions Channel!', min_values=1, max_values=1, row=1)
    async def approvedSuggestionsChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        database.execute("INSERT INTO Config VALUES (?, NULL, ?, NULL, NULL, NULL, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET approved_channel_id = ? WHERE guild_id = ?", (interaction.guild.id, select.values[0].id, select.values[0].id, interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=1, name=embed.fields[1].name, value=select.values[0].mention, inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemChannelConfigurationView())
    
    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Set Declined Suggestions Channel!', min_values=1, max_values=1, row=2)
    async def declinedSuggestionsChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        database.execute("INSERT INTO Config VALUES (?, NULL, NULL, ?, NULL, NULL, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET declined_channel_id = ? WHERE guild_id = ?", (interaction.guild.id, select.values[0].id, select.values[0].id, interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=2, name=embed.fields[2].name, value=select.values[0].mention, inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemChannelConfigurationView())
    
    @button(label="Go Back", style=ButtonStyle.blurple, row=3)
    async def goBack(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=SuggestionSystemConfigurationView())

class SuggestionSystemConfigurationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # self.add_item(AnonymousSelector())
        self.add_item(DMStatusSelector())
        self.add_item(SuggestionQueueingSelector())
        self.add_item(SuggestionThreadsSelector())

    @button(label="Done", style=ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)

    @button(label="Edit Channels", style=ButtonStyle.blurple, row=4)
    async def editChannels(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=SuggestionSystemChannelConfigurationView())

class AnonymousSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Enable", description="Enables anonymous suggestions", value=1),
            discord.SelectOption(label="Disable", description="Disables anonymous suggestions", value=0)
        ]

        super().__init__(placeholder='Configure Anonymous Suggestions', min_values=1, max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        database.execute("INSERT INTO Config VALUES (?, NULL, NULL, NULL, ?, NULL, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET anonymous = ? WHERE guild_id = ?", (interaction.guild.id, 'Enabled' if self.values[0] == '1' else 'Disabled', 'Enabled' if self.values[0] == '1' else 'Disabled', interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=3, name=embed.fields[3].name, value="✅ Enabled" if self.values[0] == '1' else "❌ Disabled", inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemConfigurationView())

class DMStatusSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Enable", description="Enables DM responses to actions", value=1),
            discord.SelectOption(label="Disable", description="Disables DM responses to actions", value=0)
        ]

        super().__init__(placeholder='Configure DM Responses', min_values=1, max_values=1, options=options, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        database.execute("INSERT INTO Config VALUES (?, NULL, NULL, NULL, NULL, ?, NULL, NULL) ON CONFLICT (guild_id) DO UPDATE SET dm_status = ? WHERE guild_id = ?", (interaction.guild.id, 'Enabled' if self.values[0] == '1' else 'Disabled', 'Enabled' if self.values[0] == '1' else 'Disabled', interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=3, name=embed.fields[3].name, value="✅ Enabled" if self.values[0] == '1' else "❌ Disabled", inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemConfigurationView())

class SuggestionQueueingSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Enable", description="Enables a queue for suggestions approval before sending them for vote", value=1),
            discord.SelectOption(label="Disable", description="Disables the queue for suggestions", value=0)
        ]

        super().__init__(placeholder='Configure Suggestion Queueing', min_values=1, max_values=1, options=options, row=2)
    
    async def callback(self, interaction: discord.Interaction):
        database.execute("INSERT INTO Config VALUES (?, NULL, NULL, NULL, NULL, NULL, ?, NULL) ON CONFLICT (guild_id) DO UPDATE SET suggestions_queue = ? WHERE guild_id = ?", (interaction.guild.id, 'Enabled' if self.values[0] == '1' else 'Disabled', 'Enabled' if self.values[0] == '1' else 'Disabled', interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=4, name=embed.fields[4].name, value="✅ Enabled" if self.values[0] == '1' else "❌ Disabled", inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemConfigurationView())

class SuggestionThreadsSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Enable", description="Enables thread creation on new suggestions", value=1),
            discord.SelectOption(label="Disable", description="Disables thread creation on new suggestions", value=0)
        ]

        super().__init__(placeholder='Configure Suggestion Threads', min_values=1, max_values=1, options=options, row=3)
    
    async def callback(self, interaction: discord.Interaction):
        database.execute("INSERT INTO Config VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, ?) ON CONFLICT (guild_id) DO UPDATE SET thread_status = ? WHERE guild_id = ?", (interaction.guild.id, 'Enabled' if self.values[0] == '1' else 'Disabled', 'Enabled' if self.values[0] == '1' else 'Disabled', interaction.guild.id,)).connection.commit()
        embed = interaction.message.embeds[0]
        embed.set_field_at(index=5, name=embed.fields[5].name, value="✅ Enabled" if self.values[0] == '1' else "❌ Disabled", inline=True)
        await interaction.response.edit_message(embed=embed, view=SuggestionSystemConfigurationView())