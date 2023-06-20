import os
import config
import sqlite3
import discord
from discord.ext import commands
from Interface.SelectMenus import RoleSelector
from Modules.Report import JoinReport, ReportButtons
from Interface.SuggestionButtons import SuggestionButtonsView

intents = discord.Intents.all()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Game(name='under development'),
            status=discord.Status.idle,
            application_id=config.APPLICATION_ID
        )

    async def setup_hook(self):
        sqlite3.connect('./Databases/data.sqlite').execute(
            '''
                CREATE TABLE IF NOT EXISTS Reports (
                    user_id INTEGER,
                    reported_user INTEGER,
                    thread_id INTEGER,
                    message_id INTEGER,
                    PRIMARY KEY (message_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Bans (
                    user_id INTEGER,
                    banned_at INTEGER,
                    expires_in INTEGER,
                    reason TEXT,
                    PRIMARY KEY(user_id))
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Warns (
                    user_id INTEGER,
                    mod_id INTEGER,
                    reason TEXT,
                    time INTEGER
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS NormalPolls (
                    poll_id TEXT,
                    question TEXT,
                    maxchoices INTEGER,
                    allowedrole INTEGER,
                    text TEXT,
                    anonymouse TEXT,
                    answer1 TEXT,
                    answer2 TEXT,
                    answer3 TEXT,
                    answer4 TEXT,
                    answer5 TEXT,
                    answer6 TEXT,
                    answer7 TEXT,
                    answer8 TEXT,
                    answer9 TEXT,
                    answer10 TEXT,
                    answer11 TEXT,
                    answer12 TEXT,
                    answer13 TEXT,
                    answer14 TEXT,
                    answer15 TEXT,
                    answer16 TEXT,
                    answer17 TEXT,
                    answer18 TEXT,
                    answer19 TEXT,
                    answer20 TEXT,
                    Primary Key (poll_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS TimedPolls (
                    poll_id TEXT,
                    question TEXT,
                    time INTEGER,
                    maxchoices INTEGER,
                    allowedrole INTEGER,
                    text TEXT,
                    anonymouse TEXT,
                    answer1 TEXT,
                    answer2 TEXT,
                    answer3 TEXT,
                    answer4 TEXT,
                    answer5 TEXT,
                    answer6 TEXT,
                    answer7 TEXT,
                    answer8 TEXT,
                    answer9 TEXT,
                    answer10 TEXT,
                    answer11 TEXT,
                    answer12 TEXT,
                    answer13 TEXT,
                    answer14 TEXT,
                    answer15 TEXT,
                    answer16 TEXT,
                    answer17 TEXT,
                    answer18 TEXT,
                    answer19 TEXT,
                    answer20 TEXT,
                    Primary Key (poll_id)
                )
            '''
        )

        sqlite3.connect("./Databases/suggestions.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS Config (
                    guild_id INTEGER,
                    suggestions_channel_id INTEGER,
                    approved_channel_id INTEGER,
                    declined_channel_id INTEGER,
                    anonymous TEXT,
                    dm_status TEXT,
                    suggestions_queue TEXT,
                    thread_status TEXT,
                    Primary Key (guild_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Queue (
                    suggestion_id TEXT,
                    user_id INTEGER,
                    suggestion TEXT,
                    anonymous TEXT,
                    Primary Key (suggestion_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Suggestions (
                    message_id INTEGER,
                    suggestion_id TEXT,
                    user_id INTEGER,
                    suggestion TEXT,
                    anonymous TEXT,
                    approver_id INTEGER,
                    Primary Key (message_id)
                )
            '''
        )

        sqlite3.connect("./Databases/activity.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS ActivityConfig (
                    guild_id INTEGER,
                    invitepoints INTEGER,
                    messagepoints INTEGER,
                    rolepoints INTEGER,
                    role_id INTEGER,
                    channelpoints INTEGER,
                    channel_id INTEGER,
                    roleandchannelpoints INTEGER,
                    role_channel_id INTEGER,
                    channel_role_id INTEGER,
                    Primary Key (guild_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS UserProfiles (
                    user_id INTEGER,
                    current_points INTEGER,
                    total_points INTEGER,
                    total_messages INTEGER,
                    message_points INTEGER,
                    total_invites INTEGER,
                    invite_points INTEGER,
                    items_shopped INTEGER,
                    Primary Key (user_id)
                )
            '''
        )

        sqlite3.connect("./Databases/tickets.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS TicketPanels (
                    panel_id TEXT,
                    message_id INTEGER,
                    role_id INTEGER,
                    channel_id INTEGER,
                    category_id INTEGER,
                    Primary Key (panel_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS UserTickets (
                    panel_id TEXT,
                    user_id INTEGER,
                    channel_id INTEGER,
                    status TEXT,
                    timestamp INTEGER
                )
            '''
        )

        sqlite3.connect("./Databases/shop.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS Items (
                    id TEXT,
                    name TEXT,
                    price INTEGER,
                    available TEXT,
                    role INTEGER,
                    Primary Key (name)
                )
            '''
        )

        database = sqlite3.connect("./Databases/reactionroles.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS ReactionRoles (
                    panel_id TEXT,
                    choices INTEGER,
                    message_id INTEGER,
                    channel_id INTEGER,
                    embed TEXT,
                    PRIMARY KEY (message_id)
                )
            '''
        )

        data = database.execute("SELECT panel_id FROM ReactionRoles").fetchall()
        self.add_view(JoinReport())
        self.add_view(ReportButtons())
        self.add_view(SuggestionButtonsView())
        if data is not None:
            for i in data:
                self.add_view(RoleSelector(i[0]))

        for filename in os.listdir("Modules"):
            if filename.endswith('.py'):
                await self.load_extension(f'Modules.{filename[:-3]}')
                print(f"Loaded {filename}")
            if filename.startswith("__"):
                pass

        await bot.tree.sync()

        for filename in os.listdir('Events'):
            if filename.endswith('.py'):
                await self.load_extension(f'Events.{filename[:-3]}')
                print(f'Loaded {filename}')
            if filename.startswith('__'):
                pass

bot = Bot()

@bot.listen()
async def on_ready():
    print(f"{bot.user} is connected to Discord, current latency is {round(bot.latency * 1000)}ms")

@bot.command(name='clear')
async def clear(ctx: commands.Context, amount: int = None):
    if amount is None:
        amount = 100

    await ctx.channel.purge(limit=amount + 1)

@bot.command(name="reload")
async def reload(ctx: commands.Context, folder: str, cog:str):
    # Reloads the file, thus updating the Cog class.
    await bot.reload_extension(f"{folder}.{cog}")
    await ctx.message.delete()
    await ctx.send(f"🔁 {cog} reloaded!", delete_after=5)

bot.run(config.TOKEN)
