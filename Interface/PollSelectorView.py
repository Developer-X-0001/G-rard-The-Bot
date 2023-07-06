import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import Select, View, Button, button, select
from Functions.GeneratePercentageBar import create_percentage_bar

database = sqlite3.connect("./Databases/polls.sqlite")

class PollSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PollSelector())

class PollSelector(Select):
    def __init__(self):
        normal_polls_data = database.execute("SELECT poll_id, question, status FROM NormalPolls").fetchall()
        timed_polls_data = database.execute("SELECT poll_id, question, status FROM TimedPolls").fetchall()

        choices = []
        for entry in normal_polls_data:
            choices.append(discord.SelectOption(label="ID: {}".format(entry[0]), emoji='🟢' if entry[2] == 'open' else '🔴', description=entry[1], value=entry[0]))
        
        for entry in timed_polls_data:
            choices.append(discord.SelectOption(label="ID: {}".format(entry[0]), emoji='🟣' if entry[2] == 'open' else '🔴', description=entry[1], value=entry[0]))
        
        choices.reverse()
        super().__init__(placeholder="Select a poll...", min_values=1, max_values=1, options=choices)

    async def callback(self, interaction: discord.Interaction):
        data = database.execute("SELECT channel_id, message_id, status, user_id, question, choices, result, maxchoices, allowedrole, anonymous, created_at, closed_at FROM NormalPolls WHERE poll_id = ?", (self.values[0],)).fetchone()
        if data is None:
            data = database.execute("SELECT channel_id, message_id, status, user_id, question, choices, result, maxchoices, allowedrole, anonymous, created_at, closed_at FROM TimedPolls WHERE poll_id = ?", (self.values[0],)).fetchone()
            time_data = database.execute("SELECT time FROM TimedPolls WHERE poll_id = ?", (self.values[0],)).fetchone()

        result = ""
        message = await interaction.guild.get_channel(data[0]).fetch_message(data[1])

        if data[2] == 'open':
            choices = {}
            users = []
            reactions = message.reactions
            for reaction in reactions:
                choices.update({f'{reaction.emoji}': reaction.count - 1})
                reaction_users = [user.id async for user in reaction.users()]
                users = list(set(users) | set(reaction_users))
            
            result = create_percentage_bar(choices=choices)
        
        else:
            result = data[6]

        settings = ""
        # if time_data:
        #     settings += "⏰ Ends in <t:{}:R>\n".format(time_data[0])
        settings += ":spy: Anonymous Poll\n" if data[9] is not None and data[9] == 1 else ""
        settings += "1 Allowed Choice" if data[7] is None or data[7] == 1 else "{} Allowed Choices".format(data[7])
        

        poll_embed = discord.Embed(
            title="Poll Overview",
            color=discord.Color.green()
        )
        poll_embed.add_field(
            name="Poll ID",
            value="`{}`".format(self.values[0]),
            inline=True
        )
        poll_embed.add_field(
            name="Status",
            value=("🟢 Open" if not time_data else '🟣 Timepoll') if data[2] != 'closed' else '🔴 Closed',
            inline=True
        )
        poll_embed.add_field(
            name="User",
            value="{}".format(interaction.guild.get_member(data[3]).mention),
            inline=True
        )
        poll_embed.add_field(
            name="Question",
            value="{}".format(data[4]),
            inline=False
        )
        poll_embed.add_field(
            name="Choices",
            value="{}".format(data[5]),
            inline=False
        )
        poll_embed.add_field(
            name="Result",
            value=result,
            inline=False
        )
        poll_embed.add_field(
            name="Settings",
            value=settings,
            inline=False
        )
        poll_embed.add_field(
            name="Channel",
            value="<#{}>".format(data[0]),
            inline=True
        )
        poll_embed.add_field(
            name="Created At",
            value="<t:{ts}:f> (<t:{ts}:R>)".format(ts=data[10]),
            inline=True
        )
        if data[11]:
            poll_embed.add_field(
                name="Closed At",
                value="<t:{ts}:f> (<t:{ts}:R>)".format(ts=data[11]),
                inline=True
            )
        
        if not data[11] and time_data:
            poll_embed.add_field(
                name="Ends At",
                value="<t:{ts}:f> (<t:{ts}:R>)".format(ts=time_data[0]),
                inline=True
            )

        poll_embed.add_field(
            name="Links",
            value="📌 [Click here to go to the message]({})".format(message.jump_url),
            inline=False
        )

        await interaction.response.edit_message(embed=poll_embed, view=PollInformationView())
        

class PollInformationView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Go Back", style=ButtonStyle.gray)
    async def go_back_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            description="Select a poll from the dropdown menu to view it's information.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=PollSelectorView())