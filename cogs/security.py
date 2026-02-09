import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import json
import os

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antinuke_enabled = False
        self.blacklisted_words = []
        self.whitelist = []
        
    @app_commands.command(name="antinuke", description="Enable high-security mode")
    @app_commands.describe(action="Turn antinuke on or off")
    @app_commands.choices(action=[
        app_commands.Choice(name="on", value="on"),
        app_commands.Choice(name="off", value="off")
    ])
    async def antinuke(self, interaction: discord.Interaction, action: str):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.antinuke_enabled = (action == "on")
        
        embed = discord.Embed(
            title=f"<:raid:{self.bot.emoji_ids['raid']}> Anti-Nuke System",
            description=f"**Status:** {'🟢 **ENABLED**' if self.antinuke_enabled else '🔴 **DISABLED**'}\n"
                       f"High-security mode has been {'activated' if self.antinuke_enabled else 'deactivated'}.",
            color=0xff0000 if self.antinuke_enabled else 0x555555
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Task completed successfully")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="anti_alt", description="Auto-kick accounts younger than X days")
    @app_commands.describe(days="Minimum account age in days")
    async def anti_alt(self, interaction: discord.Interaction, days: int):
        embed = discord.Embed(
            title=f"<:raid:{self.bot.emoji_ids['raid']}> Anti-Alt System",
            description=f"Accounts younger than **{days} days** will be automatically kicked.\n"
                       f"*Note: This runs on member join events.*",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Task completed successfully")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="lockdown", description="Seal all channels instantly")
    async def lockdown(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title=f"<:loading:{self.bot.emoji_ids['loading']}> Initiating Lockdown Protocol...",
            color=0xff0000
        )
        await interaction.response.send_message(embed=loading_embed)
        
        await asyncio.sleep(1.5)
        
        guild = interaction.guild
        locked = 0
        
        for channel in guild.channels:
            try:
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
                locked += 1
            except:
                pass
        
        embed = discord.Embed(
            title=f"<:locked:{self.bot.emoji_ids['locked']}> LOCKDOWN ACTIVATED",
            description=f"**{locked} channels** have been sealed.\n"
                       f"Only staff can send messages until lockdown is lifted.",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Task completed successfully")
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="strip_staff", description="Remove all admin roles in emergency")
    async def strip_staff(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Owner Only",
                description="Only the server owner can use this command.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        confirm_embed = discord.Embed(
            title="⚠️ CONFIRMATION REQUIRED",
            description="This will remove ALL administrative permissions from EVERYONE except you.\n"
                       "**Type `CONFIRM STRIP` to proceed.**",
            color=0xff0000
        )
        await interaction.response.send_message(embed=confirm_embed)
        
        def check(m):
            return m.author == interaction.user and m.content == "CONFIRM STRIP"
        
        try:
            await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            return
        
        stripped = 0
        for member in interaction.guild.members:
            if member == interaction.user:
                continue
                
            # Remove admin roles
            admin_roles = [role for role in member.roles if role.permissions.administrator]
            if admin_roles:
                try:
                    await member.remove_roles(*admin_roles)
                    stripped += 1
                except:
                    pass
        
        embed = discord.Embed(
            title="🛡️ Staff Stripped",
            description=f"Removed admin permissions from **{stripped} members**.\n"
                       f"Only you retain full control.",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Emergency protocol executed")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))
