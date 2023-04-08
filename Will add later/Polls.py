import re
import emoji
import config
import discord
from discord.ext import commands
from discord import app_commands

class Polls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a normal poll")
    @app_commands.describe(
        question="What is the question?",
        maxchoices="How many choices are allowed per user? (Default: 1)",
        allowedrole="Text to appear above poll (introduction, ping role, ...)",
        anonymous="Is the poll anonymous?",
        answer1="Answer 1",
        answer2="Answer 2",
        answer3="Answer 3",
        answer4="Answer 4",
        answer5="Answer 5",
        answer6="Answer 6",
        answer7="Answer 7",
        answer8="Answer 8",
        answer9="Answer 9",
        answer10="Answer 10",
        answer11="Answer 11",
        answer12="Answer 12",
        answer13="Answer 13",
        answer14="Answer 14",
        answer15="Answer 15",
        answer16="Answer 16",
        answer17="Answer 17",
        answer18="Answer 18",
        answer19="Answer 19",
        answer20="Answer 20"
    )
    @app_commands.choices(
        maxchoices=[
            app_commands.Choice(name="Unlimited", value=0),
            app_commands.Choice(name="1", value=1),
            app_commands.Choice(name="2", value=2),
            app_commands.Choice(name="3", value=3),
            app_commands.Choice(name="4", value=4),
            app_commands.Choice(name="5", value=5),
            app_commands.Choice(name="6", value=6),
            app_commands.Choice(name="7", value=7),
            app_commands.Choice(name="8", value=8),
            app_commands.Choice(name="9", value=9),
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="11", value=11),
            app_commands.Choice(name="12", value=12),
            app_commands.Choice(name="13", value=13),
            app_commands.Choice(name="14", value=14),
            app_commands.Choice(name="15", value=15),
            app_commands.Choice(name="16", value=16),
            app_commands.Choice(name="17", value=17),
            app_commands.Choice(name="18", value=18),
            app_commands.Choice(name="19", value=19),
            app_commands.Choice(name="20", value=20),
        ],
        anonymous=[
            app_commands.Choice(name="True", value=0),
            app_commands.Choice(name="False", value=1),
        ]
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        maxchoices: app_commands.Choice[int]=None,
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
        formatted_choices = []
        if answer1 is not None:
            choices.append(answer1)
        if answer2 is not None:
            choices.append(answer2)
        if answer3 is not None:
            choices.append(answer3)
        if answer4 is not None:
            choices.append(answer4)
        if answer5 is not None:
            choices.append(answer5)
        if answer6 is not None:
            choices.append(answer6)
        if answer7 is not None:
            choices.append(answer7)
        if answer8 is not None:
            choices.append(answer8)
        if answer9 is not None:
            choices.append(answer9)
        if answer10 is not None:
            choices.append(answer10)
        if answer11 is not None:
            choices.append(answer11)
        if answer12 is not None:
            choices.append(answer12)
        if answer13 is not None:
            choices.append(answer13)
        if answer14 is not None:
            choices.append(answer14)
        if answer15 is not None:
            choices.append(answer15)
        if answer16 is not None:
            choices.append(answer16)
        if answer17 is not None:
            choices.append(answer17)
        if answer18 is not None:
            choices.append(answer18)
        if answer19 is not None:
            choices.append(answer19)
        if answer20 is not None:
            choices.append(answer20)

        counter = 1
        for choice in choices:
            pattern_3 = re.compile(r'^<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>')
            emojis_3 = re.findall(pattern_3, choice)
            if choice and emoji.emoji_count(choice[0]) > 0:
                formatted_choices.append(choice)
            if emojis_3 != [] and choice.startswith(emojis_3[0]):
                formatted_choices.append(choice)
            else:
                formatted_choices.append(f'{config.ALPHABETS[counter]} {choice}')
                counter += 1
        
        total_choices = ""
        for formatted_choice in formatted_choices:
            total_choices += f"{formatted_choice}\n"

        embed = discord.Embed(
            color=discord.Color.blue()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Choices", value=total_choices, inline=False)

        await interaction.response.send_message(embed=embed)

        for i in formatted_choices:
            await interaction.message.add_reaction(i.split(' ')[0])


    @app_commands.command(name="timepoll", description="Create a timed poll with end date")
    @app_commands.describe(
        question="What is the question?",
        time="How long should the poll run? (Minutes (m), Hours (h), Days(d) | Example: 3h, 2d, 1d3h5m | Max: 7d)",
        maxchoices="How many choices are allowed per user? (Default: 1)",
        allowedrole="Text to appear above poll (introduction, ping role, ...)",
        anonymous="Is the poll anonymous?",
        answer1="Answer 1",
        answer2="Answer 2",
        answer3="Answer 3",
        answer4="Answer 4",
        answer5="Answer 5",
        answer6="Answer 6",
        answer7="Answer 7",
        answer8="Answer 8",
        answer9="Answer 9",
        answer10="Answer 10",
        answer11="Answer 11",
        answer12="Answer 12",
        answer13="Answer 13",
        answer14="Answer 14",
        answer15="Answer 15",
        answer16="Answer 16",
        answer17="Answer 17",
        answer18="Answer 18",
        answer19="Answer 19"
    )
    @app_commands.choices(
        maxchoices=[
            app_commands.Choice(name="Unlimited", value=0),
            app_commands.Choice(name="1", value=1),
            app_commands.Choice(name="2", value=2),
            app_commands.Choice(name="3", value=3),
            app_commands.Choice(name="4", value=4),
            app_commands.Choice(name="5", value=5),
            app_commands.Choice(name="6", value=6),
            app_commands.Choice(name="7", value=7),
            app_commands.Choice(name="8", value=8),
            app_commands.Choice(name="9", value=9),
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="11", value=11),
            app_commands.Choice(name="12", value=12),
            app_commands.Choice(name="13", value=13),
            app_commands.Choice(name="14", value=14),
            app_commands.Choice(name="15", value=15),
            app_commands.Choice(name="16", value=16),
            app_commands.Choice(name="17", value=17),
            app_commands.Choice(name="18", value=18),
            app_commands.Choice(name="19", value=19),
            app_commands.Choice(name="20", value=20),
        ],
        anonymous=[
            app_commands.Choice(name="True", value=0),
            app_commands.Choice(name="False", value=1),
        ]
    )
    async def timepoll(
        self,
        interaction: discord.Interaction,
        question: str,
        time: str,
        maxchoices: app_commands.Choice[int]=None,
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
        await interaction.response.send_message("Not functional yet")

async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))