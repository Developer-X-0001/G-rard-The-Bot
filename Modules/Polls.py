import re
import string
import config
import random
import sqlite3
import discord
import datetime

from discord.ext import commands
from discord import app_commands

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
        if choices == []:
            poll_embed.add_field(
                name="Choices:",
                value="👍 Yes\n👎 No",
                inline=False
            )
        else:
            formatted_choices = ""
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

    @app_commands.command(name="timepoll", description="Create a timed poll with end date.")
    @app_commands.choices(anonymous=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
        ]
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
            if choices == []:
                poll_embed.add_field(
                    name="Choices:",
                    value="👍 Yes\n👎 No",
                    inline=False
                )
            else:
                formatted_choices = ""
                for choice in choices:
                    formatted_choices += f"{config.ALPHABETS[choices.index(choice)]} {choice}\n"

                poll_embed.add_field(
                    name="Choices",
                    value=formatted_choices,
                    inline=False
                )

            settings = ""
            settings += "⏲ Ends in <t:{}:R>\n".format(round(datetime.datetime.now().timestamp()) + total_seconds + round(self.bot.latency))
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
        else:
            error_embed = discord.Embed(
                title="Invalid time specification!",
                description="**You have entered an invalid time!**\nUse a valid time code. Time codes can consist of several times ending with s (second), m (minute), h (hour), d (day) or w (week).\nExamples: 15m for 15 minutes, 1h for 1 hour, 3d for 3 days, 3d5h2m for 3 days, 5 hours and 2 minutes\n\nPS: You can click on the blue `/timepoll` command above this message to receive a copy of the used command for your poll",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))