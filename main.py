import os
import config
import sqlite3
import discord
from discord.ext import commands
from Interface.SelectMenus import RoleSelector
from Modules.Report import JoinReport, ReportButtons
from Interface.RedeemRequestView import RedeemRequestView
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
        sqlite3.connect("./Databases/settings.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS LogChannels (
                    guild_id INTEGER,
                    warn_log_channel INTEGER,
                    ban_log_channel INTEGER,
                    kick_log_channel INTEGER,
                    timeout_log_channel INTEGER,
                    PRIMARY KEY (guild_id)
                )
            '''
        )

        sqlite3.connect("./Databases/moderation.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS Bans (
                    user_id INTEGER,
                    banned_at INTEGER,
                    expires_in INTEGER,
                    mod_id INTEGER,
                    type INTEGER,
                    reason TEXT,
                    PRIMARY KEY (user_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Warns (
                    user_id INTEGER,
                    warned_at INTEGER,
                    expires_in INTEGER,
                    mod_id INTEGER,
                    type INTEGER,
                    reason TEXT,
                    PRIMARY KEY (user_id)
                )
            '''
        ).execute(
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
                CREATE TABLE IF NOT EXISTS Modlogs (
                    action_id TEXT,
                    user_id INTEGER,
                    mod_id INTEGER,
                    action TEXT,
                    action_at INTEGER,
                    reason TEXT,
                    PRIMARY KEY (action_id)
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

        sqlite3.connect("./Databases/polls.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS NormalPolls (
                    poll_id TEXT,
                    channel_id INTEGER,
                    message_id INTEGER,
                    user_id INTEGER,
                    status TEXT,
                    created_at INTEGER,
                    closed_at INTEGER,
                    question TEXT,
                    maxchoices INTEGER,
                    allowedrole INTEGER,
                    text TEXT,
                    anonymous TEXT,
                    choices TEXT,
                    result TEXT,
                    Primary Key (poll_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS TimedPolls (
                    poll_id TEXT,
                    channel_id INTEGER,
                    message_id INTEGER,
                    user_id INTEGER,
                    status TEXT,
                    created_at INTEGER,
                    closed_at INTEGER,
                    question TEXT,
                    time INTEGER,
                    maxchoices INTEGER,
                    allowedrole INTEGER,
                    text TEXT,
                    anonymous TEXT,
                    choices TEXT,
                    result TEXT,
                    Primary Key (poll_id)
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
                    image_link TEXT,
                    role INTEGER,
                    Primary Key (name)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS RedeemSettings (
                    guild_id INTEGER,
                    redeem_channel INTEGER,
                    redeem_role INTEGER,
                    Primary Key (guild_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS RedeemLogs (
                    redeemed_by INTEGER,
                    delivered_by INTEGER,
                    redeemed_at INTEGER,
                    item_id INTEGER
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS CurrentRedeems (
                    message_id INTEGER,
                    item_id INTEGER,
                    thread_id INTEGER,
                    buyer_id INTEGER,
                    handler_id INTEGER,
                    status TEXT,
                    Primary Key (message_id)
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
        self.add_view(RedeemRequestView())
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
        
        for filename in os.listdir('Tasks'):
            if filename.endswith('.py'):
                await self.load_extension(f'Tasks.{filename[:-3]}')
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
