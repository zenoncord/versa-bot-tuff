import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Bot Configuration
class EliteRedBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='?', intents=intents, help_command=None)
        self.emoji_ids = {
            'raid': 1470413892542005373,
            'mod': 1470413851349745808,
            'banned': 1470413858622410847,
            'member': 1470413855581802654,
            'success': 1470413850112163955,
            'warning': 1470413896333529099,
            'loading': 1470413862649073810,
            'locked': 1470413848937762960
        }
        
    async def setup_hook(self):
        # Load all cogs
        cogs = [
            'cogs.security',
            'cogs.courtroom',
            'cogs.moderation',
            'cogs.roblox',
            'cogs.economy',
            'cogs.social',
            'cogs.utility',
            'cogs.images'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Failed to load cog {cog}: {e}")
        
        # Sync slash commands globally
        await self.tree.sync()
        print("Slash commands synced!")

    async def on_ready(self):
        print(f'✅ {self.user} has connected to Discord!')
        print(f'📊 Serving {len(self.guilds)} guilds')
        await self.change_presence(activity=discord.Game(name="Elite Red Edition"))

# Helper function to create embeds
def create_embed(title="", description="", color=0xff0000, emoji=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    if emoji:
        embed.set_author(name=emoji)
    return embed

bot = EliteRedBot()

# Core command template
async def execute_command(ctx, func, *args, **kwargs):
    """Universal command execution with loading → success flow"""
    loading_emoji = f"<:loading:{bot.emoji_ids['loading']}>"
    success_emoji = f"<:success:{bot.emoji_ids['success']}>"
    
    # Send loading embed
    embed = create_embed(
        title=f"{loading_emoji} Processing Command...",
        color=0xff0000
    )
    message = await ctx.send(embed=embed)
    
    # Wait 1.5 seconds
    await asyncio.sleep(1.5)
    
    # Execute command function
    result = await func(*args, **kwargs)
    
    # Edit with result
    if isinstance(result, discord.Embed):
        embed = result
    elif isinstance(result, str):
        embed = create_embed(description=result, color=0xff0000)
    else:
        embed = create_embed(description="Command executed!", color=0xff0000)
    
    embed.set_footer(text=f"{success_emoji} Task completed successfully")
    await message.edit(embed=result)

# Basic ping command
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    embed = create_embed(
        title="🏓 Pong!",
        description=f"Latency: {round(bot.latency * 1000)}ms",
        color=0xff0000
    )
    embed.set_footer(text=f"<:success:{bot.emoji_ids['success']}> Task completed successfully")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = create_embed(
        title="🛡️ Elite Red Edition - Command List",
        description="**100+ Commands Organized by Section**\n\n"
                   f"<:raid:{bot.emoji_ids['raid']}> **Security & Anti-Nuke** (10 commands)\n"
                   f"<:mod:{bot.emoji_ids['mod']}> **The High Courtroom** (15 commands)\n"
                   f"<:banned:{bot.emoji_ids['banned']}> **Hard Moderation** (15 commands)\n"
                   f"<:member:{bot.emoji_ids['member']}> **Roblox & Discovery** (10 commands)\n"
                   f"<:success:{bot.emoji_ids['success']}> **Gambling & Economy** (15 commands)\n"
                   f"<:member:{bot.emoji_ids['member']}> **Social & Fun** (15 commands)\n"
                   f"<:mod:{bot.emoji_ids['mod']}> **Utility & Server Info** (10 commands)\n"
                   f"<:warning:{bot.emoji_ids['warning']}> **Image Manipulation** (10 commands)",
        color=0xff0000
    )
    embed.set_footer(text="Use ?[command] or /[command]")
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
        print("Please create a .env file with: DISCORD_TOKEN=your_token_here")
    else:
        bot.run(TOKEN)
