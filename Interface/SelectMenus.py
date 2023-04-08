import config
import sqlite3
import discord
from discord.ui import View, Select, ChannelSelect, select

database = sqlite3.connect('./Databases/reactionroles.sqlite')

class RoleSelector(View):
    def __init__(self, panel_id: str):
        super().__init__(timeout=None)
        self.add_item(GenerateSelector(panel_id=panel_id))

class GenerateSelector(Select):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        roles = [
            discord.SelectOption(label="Remove all", description='This removes all roles from this panel.', value='remove')
        ]
        data = database.execute(f"SELECT name, emoji, role_id, description FROM '{panel_id}'").fetchall()
        options_data = database.execute(f"SELECT choices FROM ReactionRoles WHERE panel_id  = '{panel_id}'").fetchone()
        for i in data:
            roles.append(discord.SelectOption(label=i[0], emoji=i[1] if i[1] else None, description=i[3] if i[3] else None, value=i[2]))

        super().__init__(placeholder='Select your role here!', min_values=1, max_values=1 if options_data is None else int(options_data[0]), options=roles, custom_id=panel_id)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'remove' and len(self.values) == 1:
            roles = []
            msg_data = database.execute("SELECT panel_id FROM ReactionRoles WHERE message_id = ?", (interaction.message.id,)).fetchone()
            data = database.execute(f"SELECT role_id FROM '{msg_data[0]}'").fetchall()
            for i in data:
                roles.append(interaction.guild.get_role(int(i[0])))
            
            for role in roles:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
            
            await interaction.response.send_message(content="```diff\n- You dropped all roles from this panel.\n```", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=RoleSelector(self.panel_id))
            return

        if len(self.values) > 1:
            work = ''
            if 'remove' in self.values:
                roles = []
                msg_data = database.execute("SELECT panel_id FROM ReactionRoles WHERE message_id = ?", (interaction.message.id,)).fetchone()
                data = database.execute(f"SELECT role_id FROM '{msg_data[0]}'").fetchall()
                for i in data:
                    roles.append(interaction.guild.get_role(int(i[0])))
                
                for role in roles:
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                
                await interaction.response.send_message(content="```diff\n- You dropped all roles from this panel.\n```", ephemeral=True)
                await interaction.followup.edit_message(message_id=interaction.message.id, view=RoleSelector(self.panel_id))
                return

            for value in self.values:
                role = interaction.guild.get_role(int(value))
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                if not role in interaction.user.roles:
                    await interaction.user.add_roles(role)
                
                work += f"{'- Removed' if role in interaction.user.roles else '+ Gave'} {role.name} role\n"
            
            await interaction.response.send_message(content=f'```diff\n{work}\n```', ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=RoleSelector(self.panel_id))

        else:
            role = interaction.guild.get_role(int(self.values[0]))
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
            if not role in interaction.user.roles:
                await interaction.user.add_roles(role)
            
            await interaction.response.send_message(content=f"```diff\n{'- Removed' if role in interaction.user.roles else '+ Gave'} {role.name} role\n```", ephemeral=True)
            await interaction.followup.edit_message(message_id=interaction.message.id, view=RoleSelector(self.panel_id))

class ChannelSelector(View):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        super().__init__(timeout=None)
    
    @select(cls=ChannelSelect, channel_types=[discord.ChannelType.text], placeholder='Select a Channel to send Reaction Roles panel', min_values=1, max_values=1)
    async def panelChannelSelect(self, interaction: discord.Interaction, select: ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)
        msg = await channel.send(embed=interaction.message.embeds[0], view=RoleSelector(self.panel_id))
        database.execute("UPDATE ReactionRoles SET message_id = ?, channel_id = ? WHERE panel_id = ?", (msg.id, channel.id, self.panel_id,)).connection.commit()
        await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully created a new reaction role panel in {channel.mention}", color=discord.Color.green()), view=None)
