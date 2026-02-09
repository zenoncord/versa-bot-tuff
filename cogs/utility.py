import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="server_info", description="Get detailed server statistics")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Get server boost level emoji
        boost_level = guild.premium_tier
        boost_emoji = ["⚪", "🟢", "🟡", "🔴"][boost_level] if boost_level < 4 else "🟣"
        
        # Calculate channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Calculate member stats
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bot_count = len([m for m in guild.members if m.bot])
        
        embed = discord.Embed(
            title=f"<:mod:{self.bot.emoji_ids['mod']}> Server Information",
            description=f"**{guild.name}**\n{guild.description or ''}",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👑 Owner", value=f"{guild.owner.mention}", inline=True)
        embed.add_field(name="🆔 Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        
        embed.add_field(name="👥 Members", 
                       value=f"**Total:** {total_members:,}\n"
                             f"**Online:** {online_members:,}\n"
                             f"**Bots:** {bot_count:,}", 
                       inline=True)
        
        embed.add_field(name="📊 Channels", 
                       value=f"**Text:** {text_channels}\n"
                             f"**Voice:** {voice_channels}\n"
                             f"**Categories:** {categories}", 
                       inline=True)
        
        embed.add_field(name="🚀 Boosts", 
                       value=f"**Level:** {boost_level}\n"
                             f"**Boosts:** {guild.premium_subscription_count}\n"
                             f"**Boosters:** {len(guild.premium_subscribers)}", 
                       inline=True)
        
        embed.add_field(name="🔐 Security", 
                       value=f"**2FA Required:** {'✅' if guild.mfa_level else '❌'}\n"
                             f"**Verification:** {str(guild.verification_level).title()}", 
                       inline=True)
        
        embed.add_field(name="🎨 Features", 
                       value="\n".join([f"• {feat.replace('_', ' ').title()}" 
                                        for feat in guild.features[:5]]), 
                       inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Task completed successfully")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="Deep dive into a user's account")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        if not user:
            user = interaction.user
        
        # Get user roles (excluding @everyone)
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        if roles:
            roles_text = " ".join(roles[-10:])  # Show last 10 roles max
            if len(roles) > 10:
                roles_text += f" (+{len(roles)-10} more)"
        else:
            roles_text = "None"
        
        # Calculate permissions
        key_permissions = []
        perms = user.guild_permissions
        if perms.administrator:
            key_permissions.append("Administrator")
        else:
            if perms.manage_guild: key_permissions.append("Manage Server")
            if perms.manage_roles: key_permissions.append("Manage Roles")
            if perms.manage_channels: key_permissions.append("Manage Channels")
            if perms.manage_messages: key_permissions.append("Manage Messages")
            if perms.kick_members: key_permissions.append("Kick Members")
            if perms.ban_members: key_permissions.append("Ban Members")
        
        embed = discord.Embed(
            title=f"<:member:{self.bot.emoji_ids['member']}> User Investigation",
            color=user.color if user.color.value != 0 else 0xff0000,
            timestamp=datetime.now()
        )
        
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
        
        embed.add_field(name="📛 Account", 
                       value=f"**Name:** {user.name}\n"
                             f"**ID:** `{user.id}`\n"
                             f"**Bot:** {'✅' if user.bot else '❌'}", 
                       inline=True)
        
        embed.add_field(name="📅 Dates", 
                       value=f"**Created:** <t:{int(user.created_at.timestamp())}:R>\n"
                             f"**Joined:** <t:{int(user.joined_at.timestamp())}:R>", 
                       inline=True)
        
        embed.add_field(name="🎨 Appearance", 
                       value=f"**Color:** `{str(user.color)}`\n"
                             f"**Avatar:** [Link]({user.avatar.url if user.avatar else 'None'})\n"
                             f"**Banner:** {'✅' if user.banner else '❌'}", 
                       inline=True)
        
        embed.add_field(name="👑 Top Role", 
                       value=f"{user.top_role.mention}\n"
                             f"**Color:** `{user.top_role.color}`", 
                       inline=True)
        
        embed.add_field(name="🔑 Key Permissions", 
                       value=", ".join(key_permissions[:5]) or "None", 
                       inline=True)
        
        embed.add_field(name="📊 Status", 
                       value=f"**Current:** {str(user.status).title()}\n"
                             f"**Activity:** {user.activity.name if user.activity else 'None'}", 
                       inline=True)
        
        embed.add_field(name="🏷️ Roles", 
                       value=f"**Count:** {len(roles)}\n"
                             f"**List:** {roles_text}", 
                       inline=False)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Investigation complete")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="uptime", description="Check how long the bot has been online")
    async def uptime(self, interaction: discord.Interaction):
        delta = datetime.now() - self.bot.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title="🕐 Bot Uptime",
            description=f"**{self.bot.user.name}** has been online for:\n\n"
                      f"**{days}** days, **{hours}** hours, **{minutes}** minutes, **{seconds}** seconds\n\n"
                      f"*Since: <t:{int(self.bot.start_time.timestamp())}:F>*",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> System operational")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    cog = Utility(bot)
    bot.start_time = datetime.now()  # Set start time when bot starts
    await bot.add_cog(cog)
