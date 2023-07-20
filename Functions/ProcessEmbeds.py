import re
import discord

async def process_embed(embed: discord.Embed):
    embed_content = ""
    if embed.title:
        embed_content += f"<h3>{embed.title}</h3>\n"
    if embed.description:
        embed_content += f"<p>{embed.description}</p>\n"
    for field in embed.fields:
        embed_content += f"<p><b>{field.name}</b>: {field.value}</p>\n"
    if embed.footer:
        embed_content += f"<p><i>{embed.footer.text}</i></p>\n"
    
    embed_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', embed_content)
    embed_content = re.sub(r'__(.*?)__', r'<u>\1</u>', embed_content)
    return embed_content