import re
import string
import config
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands
from Interface.PollSelectorView import PollSelectorView
from Functions.GeneratePercentageBar import create_percentage_bar

class Polls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/polls.sqlite")

    @app_commands.command(name="poll", description="Create a normal poll.")
    @app_commands.choices(anonymous=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
        ]
    )
    @app_commands.describe(
        question="Question for the poll",
        maxchoices="Maximum choices a user can make",
        allowedrole="Role required to vote",
        text="Message text",
        anonymous="Make poll anonymously or publicly",
        answer1="Answer 1",
        answer2="Answer ",
        answer3="Answer ",
        answer4="Answer ",
        answer5="Answer ",
        answer6="Answer ",
        answer7="Answer ",
        answer8="Answer ",
        answer9="Answer ",
        answer10="Answer ",
        answer11="Answer ",
        answer12="Answer ",
        answer13="Answer ",
        answer14="Answer ",
        answer15="Answer ",
        answer16="Answer ",
        answer17="Answer ",
        answer18="Answer ",
        answer19="Answer ",
        answer20="Answer "
    )
    async def normal_poll(
        self,
        interaction: discord.Interaction,
        question: str,
        maxchoices: int=None,
        allowedrole: discord.Role=None,
        text: str=None,
        anonymous: app_commands.Choice[int]=None,
        answer1: str=None,
        answer2: str=None,
        answer3: str=None,
        answer4: str=None,
        answer5: str=None,
        answer6: str=None,
        answer7: str=None,
        answer8: str=None,
        answer9: str=None,
        answer10: str=None,
        answer11: str=None,
        answer12: str=None,
        answer13: str=None,
        answer14: str=None,
        answer15: str=None,
        answer16: str=None,
        answer17: str=None,
        answer18: str=None,
        answer19: str=None,
        answer20: str=None
    ):
        choices = []
        choices.append(answer1) if answer1 is not None else None
        choices.append(answer2) if answer2 is not None else None
        choices.append(answer3) if answer3 is not None else None
        choices.append(answer4) if answer4 is not None else None
        choices.append(answer5) if answer5 is not None else None
        choices.append(answer6) if answer6 is not None else None
        choices.append(answer7) if answer7 is not None else None
        choices.append(answer8) if answer8 is not None else None
        choices.append(answer9) if answer9 is not None else None
        choices.append(answer10) if answer10 is not None else None
        choices.append(answer11) if answer11 is not None else None
        choices.append(answer12) if answer12 is not None else None
        choices.append(answer13) if answer13 is not None else None
        choices.append(answer14) if answer14 is not None else None
        choices.append(answer15) if answer15 is not None else None
        choices.append(answer16) if answer16 is not None else None
        choices.append(answer17) if answer17 is not None else None
        choices.append(answer18) if answer18 is not None else None
        choices.append(answer19) if answer19 is not None else None
        choices.append(answer20) if answer20 is not None else None

        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(9)]).upper()

        if maxchoices is not None:
            if maxchoices > len(choices):
                maxchoices = len(choices)
            
            if maxchoices <= 0:
                maxchoices = 1
            
            else:
                maxchoices = maxchoices

        poll_embed = discord.Embed(
            color=discord.Color.blue()
        )
        poll_embed.add_field(
            name="Question",
            value=question,
            inline=False
        )
        formatted_choices = ""
        if choices == []:
            poll_embed.add_field(
                name="Choices:",
                value="👍 Yes\n👎 No",
                inline=False
            )
            formatted_choices = "👍 Yes\n👎 No"
        else:
            
            for choice in choices:
                formatted_choices += f"{config.ALPHABETS[choices.index(choice)]} {choice}\n"

            poll_embed.add_field(
                name="Choices",
                value=formatted_choices,
                inline=False
            )

        settings = ""
        settings += ":spy: Anonymous Poll\n" if anonymous is not None and anonymous.value == 1 else ""
        settings += "1 Allowed Choice" if maxchoices is None or maxchoices == 1 else "{} Allowed Choices".format(maxchoices)

        poll_embed.add_field(
            name="Settings",
            value=settings,
            inline=False
        )
        if allowedrole is not None:
            poll_embed.add_field(
                name="Allowed Role:",
                value=allowedrole.mention,
                inline=False
            )
        
        poll_embed.set_footer(text="Poll ID: {}".format(id))

        await interaction.response.send_message(content=text if text is not None else None, embed=poll_embed)
        message = await interaction.original_response()

        if choices == []:
            await message.add_reaction('👍')
            await message.add_reaction('👎')
        
        else:
            for choice in choices:
                await message.add_reaction(config.ALPHABETS[choices.index(choice)])
        
        self.database.execute("INSERT INTO NormalPolls VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, NULL)",
            (
                id,
                interaction.channel.id,
                message.id,
                interaction.user.id,
                'open',
                round(datetime.datetime.now().timestamp()),
                question,
                1 if not maxchoices else maxchoices,
                allowedrole.id if allowedrole else None,
                text if text else None,
                True if anonymous is not None and anonymous.value == 1 else False,
                formatted_choices,
            )
        ).connection.commit()


    @app_commands.command(name="timepoll", description="Create a timed poll with end date.")
    @app_commands.choices(anonymous=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
        ]
    )
    @app_commands.describe(
        question="Question for the poll",
        time="Time allowed for this poll",
        maxchoices="Maximum choices a user can make",
        allowedrole="Role required to vote",
        text="Message text",
        anonymous="Make poll anonymously or publicly",
        answer1="Answer 1",
        answer2="Answer ",
        answer3="Answer ",
        answer4="Answer ",
        answer5="Answer ",
        answer6="Answer ",
        answer7="Answer ",
        answer8="Answer ",
        answer9="Answer ",
        answer10="Answer ",
        answer11="Answer ",
        answer12="Answer ",
        answer13="Answer ",
        answer14="Answer ",
        answer15="Answer ",
        answer16="Answer ",
        answer17="Answer ",
        answer18="Answer ",
        answer19="Answer "
    )
    async def time_poll(
        self,
        interaction: discord.Interaction,
        question: str,
        time: str,
        maxchoices: int=None,
        allowedrole: discord.Role=None,
        text: str=None,
        anonymous: app_commands.Choice[int]=None,
        answer1: str=None,
        answer2: str=None,
        answer3: str=None,
        answer4: str=None,
        answer5: str=None,
        answer6: str=None,
        answer7: str=None,
        answer8: str=None,
        answer9: str=None,
        answer10: str=None,
        answer11: str=None,
        answer12: str=None,
        answer13: str=None,
        answer14: str=None,
        answer15: str=None,
        answer16: str=None,
        answer17: str=None,
        answer18: str=None,
        answer19: str=None
    ):
        pattern = r'(\d+s)?(\d+m)?(\d+h)?(\d+d)?'
        match = re.match(pattern, time)

        if match:
            seconds = int(match.group(1)[:-1]) if match.group(1) else 0
            minutes = int(match.group(2)[:-1]) if match.group(2) else 0
            hours = int(match.group(3)[:-1]) if match.group(3) else 0
            days = int(match.group(4)[:-1]) if match.group(4) else 0

            total_seconds = seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60 * 60)

            choices = []
            choices.append(answer1) if answer1 is not None else None
            choices.append(answer2) if answer2 is not None else None
            choices.append(answer3) if answer3 is not None else None
            choices.append(answer4) if answer4 is not None else None
            choices.append(answer5) if answer5 is not None else None
            choices.append(answer6) if answer6 is not None else None
            choices.append(answer7) if answer7 is not None else None
            choices.append(answer8) if answer8 is not None else None
            choices.append(answer9) if answer9 is not None else None
            choices.append(answer10) if answer10 is not None else None
            choices.append(answer11) if answer11 is not None else None
            choices.append(answer12) if answer12 is not None else None
            choices.append(answer13) if answer13 is not None else None
            choices.append(answer14) if answer14 is not None else None
            choices.append(answer15) if answer15 is not None else None
            choices.append(answer16) if answer16 is not None else None
            choices.append(answer17) if answer17 is not None else None
            choices.append(answer18) if answer18 is not None else None
            choices.append(answer19) if answer19 is not None else None

            id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(9)]).upper()

            if maxchoices is not None:
                if maxchoices > len(choices):
                    maxchoices = len(choices)
                
                if maxchoices <= 0:
                    maxchoices = 1
                
                else:
                    maxchoices = maxchoices

            poll_embed = discord.Embed(
                color=discord.Color.blue()
            )
            poll_embed.add_field(
                name="Question",
                value=question,
                inline=False
            )
            formatted_choices = ""
            if choices == []:
                poll_embed.add_field(
                    name="Choices:",
                    value="👍 Yes\n👎 No",
                    inline=False
                )
                formatted_choices = "👍 Yes\n👎 No"
            else:
                for choice in choices:
                    formatted_choices += f"{config.ALPHABETS[choices.index(choice)]} {choice}\n"

                poll_embed.add_field(
                    name="Choices",
                    value=formatted_choices,
                    inline=False
                )

            settings = ""
            settings += "⏰ Ends in <t:{}:R>\n".format(round(datetime.datetime.now().timestamp()) + total_seconds + round(self.bot.latency))
            settings += ":spy: Anonymous Poll\n" if anonymous is not None and anonymous.value == 1 else ""
            settings += "1 Allowed Choice" if maxchoices is None or maxchoices == 1 else "{} Allowed Choices".format(maxchoices)

            poll_embed.add_field(
                name="Settings",
                value=settings,
                inline=False
            )
            if allowedrole is not None:
                poll_embed.add_field(
                    name="Allowed Role:",
                    value=allowedrole.mention,
                    inline=False
                )
            
            poll_embed.set_footer(text="Poll ID: {}".format(id))

            await interaction.response.send_message(content=text if text is not None else None, embed=poll_embed)
            message = await interaction.original_response()

            if choices == []:
                await message.add_reaction('👍')
                await message.add_reaction('👎')
            
            else:
                for choice in choices:
                    await message.add_reaction(config.ALPHABETS[choices.index(choice)])
            
            self.database.execute("INSERT INTO TimedPolls VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, NULL)",
            (
                id,
                interaction.channel.id,
                message.id,
                interaction.user.id,
                'open',
                round(datetime.datetime.now().timestamp()),
                question,
                round(datetime.datetime.now().timestamp()) + total_seconds,
                1 if not maxchoices else maxchoices,
                allowedrole.id if allowedrole else None,
                text if text else None,
                True if anonymous is not None and anonymous.value == 1 else False,
                formatted_choices,
            )
        ).connection.commit()
            
        else:
            error_embed = discord.Embed(
                title="Invalid time specification!",
                description="**You have entered an invalid time!**\nUse a valid time code. Time codes can consist of several times ending with s (second), m (minute), h (hour), d (day) or w (week).\nExamples: 15m for 15 minutes, 1h for 1 hour, 3d for 3 days, 3d5h2m for 3 days, 5 hours and 2 minutes\n\nPS: You can click on the blue `/timepoll` command above this message to receive a copy of the used command for your poll",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @app_commands.command(name="closepoll", description="Close a poll so that no more votes are counted")
    @app_commands.describe(
        poll_id="ID of the poll"
    )
    async def close_poll(self, interaction: discord.Interaction, poll_id: str):
        timed_poll_data = self.database.execute("SELECT channel_id, message_id, user_id, time, maxchoices, allowedrole, anonymous FROM TimedPolls WHERE poll_id = ?", (poll_id,)).fetchone()
        if timed_poll_data is None:
            normal_poll_data = self.database.execute("SELECT channel_id, message_id, user_id, maxchoices, allowedrole, anonymous FROM NormalPolls WHERE poll_id = ?", (poll_id,)).fetchone()
            channel = interaction.guild.get_channel(normal_poll_data[0])
            message = await channel.fetch_message(normal_poll_data[1])
            user = interaction.guild.get_member(normal_poll_data[2])
            reactions = message.reactions
            allowedrole = interaction.guild.get_role(normal_poll_data[4])
            anonymous = True if normal_poll_data[5] and normal_poll_data[5] == 'true' else False
            maxchoices = '1 Allowed Choice' if normal_poll_data[3] is None or normal_poll_data[3] == 1 else '{} Allowed Choices'.format(normal_poll_data[3])
            poll_embed = message.embeds[0]
            poll_embed.color = discord.Color.red()

            choices = {}
            users = []
            for reaction in reactions:
                choices.update({f'{reaction.emoji}': reaction.count - 1})
                reaction_users = [user.id async for user in reaction.users()]
                users = list(set(users) | set(reaction_users))

            users.remove(self.bot.user.id) if self.bot.user.id in users else None
            poll_embed.insert_field_at(
                index=2,
                name="Final Result:",
                value=f"{create_percentage_bar(choices=choices)}{len(users)} user{'s' if len(users) > 1 else ''} voted",
                inline=False
            )
            poll_embed.set_field_at(
                index=3,
                name="Settings:",
                value=f"{poll_embed.fields[3].value}\n\n🔒 No other votes allowed",
                inline=False
            )

            await message.edit(embed=poll_embed)
            await message.clear_reactions()

            await interaction.response.send_message(embed=discord.Embed(title="Poll Closed", description="The poll with ID **{}** was closed!\nNo more votes are allowed and the result is now displayed in the poll.".format(poll_id), color=discord.Color.purple()), ephemeral=True)
            self.database.execute("UPDATE NormalPolls SET status = ?, closed_at = ?, result = ? WHERE poll_id = ?", ('closed', round(datetime.datetime.now().timestamp()), create_percentage_bar(choices=choices), poll_id,)).connection.commit()
        else:
            print()
    
    @close_poll.autocomplete('poll_id')
    async def close_poll_autocomplete(self, interaction: discord.Interaction, current: str):
        normal_polls_data = self.database.execute("SELECT poll_id FROM NormalPolls WHERE status = ?", ('open',)).fetchall()
        timed_polls_data = self.database.execute("SELECT poll_id FROM TimedPolls WHERE status = ?", ('open',)).fetchall()

        data = normal_polls_data + timed_polls_data

        return [app_commands.Choice(name='ID: {}'.format(entry[0]), value=entry[0]) for entry in data if current in entry[0]]

    @app_commands.command(name="listpolls", description="Show the polls from the current server.")
    @app_commands.describe(
        poll_id="ID of the poll"
    )
    async def list_polls(self, interaction: discord.Interaction, poll_id: str=None):
        if poll_id is None:
            embed = discord.Embed(
                description="Select a poll from the dropdown menu to view it's information.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, view=PollSelectorView(), ephemeral=True)
        
        else:
            data = self.database.execute("SELECT channel_id, message_id, status, user_id, question, choices, result, maxchoices, allowedrole, anonymous, created_at, closed_at FROM NormalPolls WHERE poll_id = ?", (self.values[0],)).fetchone()
            if data is None:
                data = self.database.execute("SELECT channel_id, message_id, status, user_id, question, choices, result, maxchoices, allowedrole, anonymous, created_at, closed_at FROM TimedPolls WHERE poll_id = ?", (self.values[0],)).fetchone()
                time_data = self.database.execute("SELECT time FROM TimedPolls WHERE poll_id = ?", (self.values[0],)).fetchone()

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

            await interaction.response.send_message(embed=poll_embed, ephemeral=True)
    
    @list_polls.autocomplete('poll_id')
    async def list_polls_autocomplete(self, interaction: discord.Interaction, current: str):
        normal_polls_data = self.database.execute("SELECT poll_id FROM NormalPolls WHERE status = ?", ('open',)).fetchall()
        timed_polls_data = self.database.execute("SELECT poll_id FROM TimedPolls WHERE status = ?", ('open',)).fetchall()

        data = normal_polls_data + timed_polls_data

        return [app_commands.Choice(name='ID: {}'.format(entry[0]), value=entry[0]) for entry in data if current in entry[0]]

async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))