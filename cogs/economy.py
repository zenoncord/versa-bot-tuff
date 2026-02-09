import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import random
from datetime import datetime
import os

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/economy.json"
        self.user_data = self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.user_data, f, indent=4)
    
    def get_user_data(self, user_id):
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {
                "wallet": 1000,
                "bank": 0,
                "daily_streak": 0,
                "last_daily": None,
                "inventory": []
            }
        return self.user_data[str(user_id)]
    
    @app_commands.command(name="balance", description="Check your wallet and bank balance")
    async def balance(self, interaction: discord.Interaction):
        data = self.get_user_data(interaction.user.id)
        
        embed = discord.Embed(
            title=f"<:success:{self.bot.emoji_ids['success']}> Financial Report",
            description=f"**Account Holder:** {interaction.user.mention}\n\n"
                      f"💰 **Wallet:** ${data['wallet']:,}\n"
                      f"🏦 **Bank:** ${data['bank']:,}\n"
                      f"📈 **Total:** ${data['wallet'] + data['bank']:,}\n\n"
                      f"*Daily streak: {data['daily_streak']} days*",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Task completed successfully")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily credits")
    async def daily(self, interaction: discord.Interaction):
        data = self.get_user_data(interaction.user.id)
        now = datetime.now().isoformat()
        
        # Check if daily was already claimed today
        if data['last_daily']:
            last_date = datetime.fromisoformat(data['last_daily']).date()
            if last_date == datetime.now().date():
                embed = discord.Embed(
                    title="⏰ Already Claimed",
                    description="You've already claimed your daily credits today!\n"
                              f"Come back tomorrow for more.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Calculate reward
        base_reward = 1000
        streak_bonus = data['daily_streak'] * 50
        total = base_reward + streak_bonus
        
        # Update data
        data['wallet'] += total
        data['daily_streak'] += 1
        data['last_daily'] = now
        self.save_data()
        
        embed = discord.Embed(
            title=f"<:success:{self.bot.emoji_ids['success']}> Daily Reward Claimed!",
            description=f"**Amount:** ${total:,}\n"
                      f"**Breakdown:**\n"
                      f"• Base: ${base_reward:,}\n"
                      f"• Streak Bonus: ${streak_bonus:,}\n\n"
                      f"**New Balance:** ${data['wallet']:,}\n"
                      f"**Streak:** {data['daily_streak']} days 🔥",
            color=0xff0000
        )
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Come back tomorrow!")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="blackjack", description="Play 21 against the bot")
    @app_commands.describe(bet="Amount to bet")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        data = self.get_user_data(interaction.user.id)
        
        if bet <= 0:
            embed = discord.Embed(
                title="❌ Invalid Bet",
                description="Bet must be greater than 0.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if data['wallet'] < bet:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"You only have ${data['wallet']:,} in your wallet.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Loading message
        embed = discord.Embed(
            title=f"<:loading:{self.bot.emoji_ids['loading']}> Dealing Cards...",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(1.5)
        
        # Simple blackjack logic
        player_cards = [random.randint(1, 11) for _ in range(2)]
        dealer_cards = [random.randint(1, 11) for _ in range(2)]
        
        player_total = sum(player_cards)
        dealer_total = sum(dealer_cards)
        
        # Determine winner
        if player_total == 21:
            result = "BLACKJACK! You win 3:2!"
            multiplier = 2.5
        elif player_total > 21:
            result = "BUST! You lose."
            multiplier = 0
        elif dealer_total > 21:
            result = "Dealer busts! You win!"
            multiplier = 2
        elif player_total > dealer_total:
            result = "You win!"
            multiplier = 2
        elif player_total < dealer_total:
            result = "You lose."
            multiplier = 0
        else:
            result = "Push! It's a tie."
            multiplier = 1
        
        winnings = int(bet * multiplier)
        data['wallet'] += winnings - bet  # Adjust for bet
        self.save_data()
        
        # Create result embed
        embed = discord.Embed(
            title="♠️♥️♣️♦️ BLACKJACK ♠️♥️♣️♦️",
            description=f"**Bet:** ${bet:,}\n\n"
                      f"**Your Hand:** {player_cards} = {player_total}\n"
                      f"**Dealer's Hand:** {dealer_cards[0]} + ? = ?+\n\n"
                      f"**Result:** {result}\n"
                      f"**Payout:** ${winnings:,}",
            color=0x00ff00 if multiplier > 1 else 0xff0000 if multiplier == 0 else 0xffff00
        )
        
        if player_total == 21:
            embed.add_field(name="🎰", value="**BLACKJACK!** Natural 21!")
        
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> New balance: ${data['wallet']:,}")
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="rob", description="Attempt to steal from another user")
    @app_commands.describe(user="User to rob")
    async def rob(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            embed = discord.Embed(
                title="🤔 Self Robbery?",
                description="You can't rob yourself!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        robber_data = self.get_user_data(interaction.user.id)
        target_data = self.get_user_data(user.id)
        
        if target_data['wallet'] < 100:
            embed = discord.Embed(
                title="💸 Too Poor",
                description=f"{user.mention} doesn't have enough cash to rob (minimum $100).",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        success_chance = 0.4  # 40% success rate
        if random.random() < success_chance:
            # Successful robbery
            amount = random.randint(50, min(500, target_data['wallet']))
            robber_data['wallet'] += amount
            target_data['wallet'] -= amount
            self.save_data()
            
            embed = discord.Embed(
                title="🎭 Successful Robbery!",
                description=f"You stole **${amount:,}** from {user.mention}!\n\n"
                          f"**Your new balance:** ${robber_data['wallet']:,}\n"
                          f"**Their remaining:** ${target_data['wallet']:,}",
                color=0x00ff00
            )
        else:
            # Failed robbery - fine
            fine = random.randint(100, 500)
            robber_data['wallet'] -= fine
            robber_data['wallet'] = max(0, robber_data['wallet'])
            self.save_data()
            
            embed = discord.Embed(
                title="🚓 Caught Red-Handed!",
                description=f"You were caught trying to rob {user.mention}!\n"
                          f"**Fine:** ${fine:,}\n\n"
                          f"**Your new balance:** ${robber_data['wallet']:,}",
                color=0xff0000
            )
        
        embed.set_footer(text=f"<:success:{self.bot.emoji_ids['success']}> Crime doesn't pay... usually")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
