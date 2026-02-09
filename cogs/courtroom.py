import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime
import json

class Courtroom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_cases = {}
        self.jailed_users = {}
        
    @app_commands.command(name="sue", description="Open a formal trial against a user")
    @app_commands.describe(user="User to sue", reason="Reason for the lawsuit")
    async def sue(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        case_id = f"CASE-{interaction.guild.id}-{len(self.active_cases)+1:04d}"
        
        # Create trial thread
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        try:
            thread = await interaction.channel.create_thread(
                name=f"Trial: {user.name} vs {interaction.user.name}",
                type=discord.ChannelType.public_thread,
                reason=f"Court case #{case_id}"
            )
            
            # Set permissions
            for target, overwrite in overwrites.items():
                await thread.set_permissions(target, overwrite=overwrite)
            
            # Add case to active cases
            self.active_cases[case_id] = {
                "plaintiff": interaction.user.id,
                "defendant": user.id,
                "reason": reason,
                "thread_id": thread.id,
                "status": "active",
                "opened": datetime.now().isoformat()
            }
            
            embed = discord.Embed(
                title=f"<:mod:{self.bot.emoji_ids['mod']}> Court Case Opened",
                description=f"**Case ID:** {case_id}\n"
                          f"**Plaintiff:** {interaction.user.mention}\n"
                          f"**Defendant:** {user.mention}\n"
                          f"**Reason:** {reason}\n\n"
                          f"Trial thread: {thread.mention}",
                color=0xff0000
            )
            embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Court is now in session")
            await interaction.response.send_message(embed=embed)
            
            # Send initial message in thread
            thread_embed = discord.Embed(
                title="⚖️ THE HIGH COURTROOM",
                description=f"**Case {case_id} is now in session!**\n\n"
                          f"👨‍⚖️ **Judge:** {interaction.user.mention}\n"
                          f"⚖️ **Defendant:** {user.mention}\n"
                          f"📜 **Charge:** {reason}\n\n"
                          f"Use `/objection` for dramatic interruptions\n"
                          f"Use `/verdict` when ready to deliver judgment",
                color=0xff0000
            )
            await thread.send(embed=thread_embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Court Error",
                description=f"Failed to create trial: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="jail", description="Send a user to the jail channel")
    @app_commands.describe(user="User to jail", reason="Reason for jailing")
    async def jail(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Contempt of court"):
        # Check if jail channel exists
        jail_channel = discord.utils.get(interaction.guild.channels, name="jail")
        if not jail_channel:
            try:
                jail_channel = await interaction.guild.create_text_channel(
                    "jail",
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
                    }
                )
            except:
                embed = discord.Embed(
                    title="❌ Jail Error",
                    description="Could not create jail channel. Check bot permissions.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Timeout the user
        try:
            await user.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=24))
        except:
            pass
        
        self.jailed_users[user.id] = {
            "jailed_by": interaction.user.id,
            "reason": reason,
            "time": datetime.now().isoformat()
        }
        
        embed = discord.Embed(
            title=f"<:locked:{self.bot.emoji_ids['locked']}> User Jailed",
            description=f"**Prisoner:** {user.mention}\n"
                      f"**Cell:** {jail_channel.mention}\n"
                      f"**Sentence:** 24 hours\n"
                      f"**Reason:** {reason}\n\n"
                      f"*They can view but not speak in the jail channel.*",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Justice served")
        await interaction.response.send_message(embed=embed)
        
        # Send jail message
        jail_embed = discord.Embed(
            title="🔒 YOU HAVE BEEN JAILED",
            description=f"**Reason:** {reason}\n"
                      f"**Sentence:** 24 hours\n"
                      f"**Judge:** {interaction.user.mention}\n\n"
                      f"You can view this channel but cannot speak.\n"
                      f"Use `/bail` to pay for early release.",
            color=0xff0000
        )
        await jail_channel.send(content=user.mention, embed=jail_embed)
    
    @app_commands.command(name="objection", description="Dramatic trial interruption")
    async def objection(self, interaction: discord.Interaction):
        objection_gifs = [
            "https://i.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "https://i.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
            "https://i.giphy.com/media/26tknCqiJrBQG6DrC/giphy.gif"
        ]
        
        import random
        gif = random.choice(objection_gifs)
        
        embed = discord.Embed(
            title="⚖️ OBJECTION!",
            description=f"{interaction.user.mention} dramatically interrupts the proceedings!",
            color=0xff0000
        )
        embed.set_image(url=gif)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="community_service", description="Force a user to type a sentence")
    @app_commands.describe(user="User to punish", sentence="Sentence to repeat")
    async def community_service(self, interaction: discord.Interaction, user: discord.Member, sentence: str):
        embed = discord.Embed(
            title="⚖️ Community Service Order",
            description=f"{user.mention} must type the following sentence **100 times** to speak again:\n\n"
                      f"*\"{sentence}\"*\n\n"
                      f"They have 10 minutes to complete this task.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
        
        # Store the task
        await self.bot.get_cog('Moderation').mute(interaction, user, 600)  # 10 minute mute
        
        # Create a DM task
        try:
            dm = await user.create_dm()
            await dm.send(
                f"**COMMUNITY SERVICE NOTICE**\n\n"
                f"You have been ordered to type the following sentence 100 times:\n"
                f"```{sentence}```\n"
                f"You have 10 minutes. Each message must be exactly as shown above."
            )
        except:
            pass

async def setup(bot):
    await bot.add_cog(Courtroom(bot))
