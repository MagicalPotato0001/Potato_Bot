import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import random
import json

class HitButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.red, label="Hit")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user.id
        deck = self.cog.player_decks[user]
        card = deck.pop(0)
        if (self.cog.player_hands[user] + int(card[1])) > 21:
            await interaction.followup.send(f"{interaction.user.mention} Bust! You lose {self.player_bets[user]}")
        else:
            embed = discord.Embed(title=f"{interaction.user.name}'s Blackjack Game", color=discord.Color.blue())
            embed.add_field(name="Dealer's Hand", value="?," + self.cog.dealer_hands[user][1], inline=True)
            player_hand = [(card + ",") for card in self.cog.player_hands[user]]
            embed.add_field(name="Dealer's Hand", value=player_hand, inline=True)


class StandButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.grey, label="Stand")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user.id
        await interaction.followup.send(f"{interaction.user.mention} Video queue not large enough!")

class BlackjackView(View):
    def __init__(self, cog):
        super().__init__()
        self.add_item(HitButton(cog))
        self.add_item(StandButton(cog))

class GambleCog(commands.Cog):
    def __init__(self,
                 bot = None,
                 name = "Potato Bot",
                 player_save_file = "cogs/players.json",
                 server_save_file = "cogs/server_settings.json"):
        self.bot = bot
        self.name = name
        self.suits = ["♠️", "♥️", "♦️", "♣️"]
        self.ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.deck = [(suit + rank) for suit in self.suits for rank in self.ranks]
        self.player_decks = {}
        self.dealer_hands = {}
        self.player_hands = {}
        self.player_bets = {}

        self.psave_file = player_save_file
        self.loaded_players = None
        self.load_players()

        self.server_save_file = server_save_file


    # Function to save player data to a JSON file
    def save_players(self, players_data):
        try:
            with open(self.psave_file, 'w') as file:
                json.dump(players_data, file)
        except Exception as e:
            print(f"[GambleCog] error saving players: {e}")

    # Function to load player data from a JSON file and update it with new members
    def load_players(self):
        try:
            with open(self.psave_file, 'r') as file:
                file_contents = file.read()
                if file_contents:
                    self.loaded_players = json.loads(file_contents)
                else:
                    self.loaded_players = {}
        except FileNotFoundError:
            self.loaded_players = {}
            print(f"[GambleCog] Error finding player save: {e}")
        except json.JSONDecodeError as e:
            print(f"[GambleCog] Error loading players: {e}")
            self.loaded_players = {}
        # Save the updated players back to the file
        self.save_players(self.loaded_players)

    async def update_players(self):
        try:
            for guild in self.bot.guilds:
                for member in guild.members:
                    member_id = str(member.id)
                    if member_id not in self.loaded_players:
                        print(f"[GambleCog] {member.display_name} Added!")
                        self.loaded_players[member_id] = {'money': 10000, 'wins': 0, 'losses': 0}
            self.save_players(self.loaded_players)
        except Exception as e:
            print(f"[GableCog] Error updating player base: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[GambleCog] Loaded")
        self.bot.loop.create_task(self.update_players())

    @app_commands.command(name="stats", description="Show your gambling stats!")
    async def stats(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)  # Get the user ID of the person who invoked the command

        # Check if the user exists in the players dictionary
        if user_id in self.loaded_players:
            user_data = self.loaded_players[user_id]

            # Create an embed to display the stats
            embed = discord.Embed(title=f"{interaction.user.name}'s Gambling Stats", color=discord.Color.blue())
            embed.set_thumbnail(url=interaction.user.display_avatar.url)  # Set the user's profile picture as thumbnail
            embed.add_field(name="Money", value=user_data.get('money', 0), inline=True)
            embed.add_field(name="Wins", value=user_data.get('wins', 0), inline=True)
            embed.add_field(name="Losses", value=user_data.get('losses', 0), inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=self.bot.user.avatar.url)

            await interaction.response.send_message(embed=embed)
        else:
            # Send a message if the user is not found in the players dictionary
            await interaction.response.send_message("You don't have any gambling stats yet!")

    @app_commands.command(name="blackjack", description="Play a game of blackjack!")
    async def blackjack(self, interaction: discord.Interaction, bet: float):
        await interaction.response.send_message("Coming Soon!")

    @app_commands.command(name="stakes", description="Stake a bet against your friends!")
    async def blackjack(self, interaction: discord.Interaction, bet: float):
        await interaction.response.send_message("Coming Soon!")

