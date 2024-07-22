import discord
from discord.ext import commands
from discord import app_commands

class BasicCog(commands.Cog):
    def __init__(self,
                 bot = None,
                 verbose = True,
                 channels = [],
                 name = "Potato Bot",):
        self.bot = bot
        self.verbose = verbose
        self.channels = channels
        self.name = name
    
    @commands.Cog.listener()
    async def on_ready(self):
        if self.channels:
            for channel_id in self.channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(f"[{self.name}] Started!")
        print("[BasicCog] Loaded")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.verbose:
            print(f"[{message.author}] {message.content}")
