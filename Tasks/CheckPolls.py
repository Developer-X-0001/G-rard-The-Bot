import config
import sqlite3
import discord
import datetime

from discord.ext import commands, tasks
from Functions.GeneratePercentageBar import create_percentage_bar

database = sqlite3.connect("./Databases/polls.sqlite")

class CheckPolls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_timed_polls.start()

    @tasks.loop(seconds=1)
    async def check_timed_polls(self):
        data = database.execute("SELECT poll_id, time FROM TimedPolls WHERE status = ?", ('open',)).fetchall()
        guild = self.bot.get_guild(config.GUILD_ID)
        for entry in data:
            current_time = round(datetime.datetime.now().timestamp())
            poll_time = entry[1]

            if current_time >= poll_time:
                timed_poll_data = database.execute("SELECT channel_id, message_id, user_id, time, maxchoices, allowedrole, anonymous FROM TimedPolls WHERE poll_id = ?", (entry[0],)).fetchone()
                channel = guild.get_channel(timed_poll_data[0])
                message = await channel.fetch_message(timed_poll_data[1])
                user = guild.get_member(timed_poll_data[2])
                reactions = message.reactions
                allowedrole = guild.get_role(timed_poll_data[4])
                anonymous = True if timed_poll_data[5] and timed_poll_data[5] == 'true' else False
                maxchoices = '1 Allowed Choice' if timed_poll_data[4] is None or timed_poll_data[4] == 1 else '{} Allowed Choices'.format(timed_poll_data[4])
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
                    value=f"⏰ Poll already ended (<t:{current_time}:R>)\n{maxchoices}\n\n🔒 No other votes allowed",
                    inline=False
                )

                await message.edit(embed=poll_embed)
                await message.clear_reactions()
                database.execute("UPDATE TimedPolls SET status = ?, closed_at = ?, result = ? WHERE poll_id = ?", ('closed', round(datetime.datetime.now().timestamp()), create_percentage_bar(choices=choices), entry[0],)).connection.commit()

            else:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckPolls(bot))