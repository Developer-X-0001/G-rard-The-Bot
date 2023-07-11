import config
import sqlite3
import discord

from discord.ext import commands

database = sqlite3.connect("./Databases/polls.sqlite")

class RawReactionActionEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = guild.get_member(payload.user_id)

        if user.bot:
            return

        if message.embeds:
            data = database.execute("SELECT maxchoices FROM NormalPolls WHERE poll_id = ?", (message.embeds[0].footer.text[9:],)).fetchone()
            if data is None:
                data = database.execute("SELECT maxchoices FROM TimedPolls WHERE poll_id = ?", (message.embeds[0].footer.text[9:],)).fetchone()
                if data is None:
                    maxchoices = data[0]
                    reactions = message.reactions
                    user_reactions = []
                    for reaction in reactions:
                        users = [user.id async for user in reaction.users()]
                        if payload.user_id in users:
                            user_reactions.append(reaction)
                    
                        if payload.emoji.name == reaction.emoji:
                            user_reactions.remove(reaction)
                    
                    if (len(user_reactions)) == maxchoices:
                        to_remove = user_reactions[len(user_reactions)-1:]
                        
                        for i in to_remove:
                            await i.remove(user)

            if data is not None:
                maxchoices = data[0]
                reactions = message.reactions
                user_reactions = []
                for reaction in reactions:
                    users = [user.id async for user in reaction.users()]
                    if payload.user_id in users:
                        user_reactions.append(reaction)
                
                    if payload.emoji.name == reaction.emoji:
                        user_reactions.remove(reaction)
                
                if (len(user_reactions)) == maxchoices:
                    to_remove = user_reactions[len(user_reactions)-1:]
                    
                    for i in to_remove:
                        await i.remove(user)
            else:
                return

        else:
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(RawReactionActionEvent(bot))