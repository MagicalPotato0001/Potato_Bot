import discord
from discord.ext import commands
from cogs.basic_cog import BasicCog
from cogs.music_cog import MusicCog
#from cogs.gamble_cog import GambleCog
import argparse
import asyncio
import json
import os

# Argument parser setup
parser = argparse.ArgumentParser(description="A simple Discord bot")
parser.add_argument('--token', type=str, help='The Discord bot token')
args = parser.parse_args()
arg_token = args.token

class PotatoBot(commands.Bot):
    def __init__(self, 
                 command_prefix = "!", 
                 intents = discord.Intents.all(),
                 chat_channels = [],
                 guild_channels = []):
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.synced = False
        self.voice_channel = {}
        self.chat_channels = chat_channels
        self.guild_channels = guild_channels

    async def sync_bot(self):
        await self.wait_until_ready()
        try:
            await self.tree.sync()
        except Exception as e:
            print(f"Syncing failed: {e}")
        for guild_id in self.guild_channels:
            try:
                await self.tree.sync(guild= discord.Object(id=guild_id))
                print(f"Synced guild: {guild_id}")
            except Exception as e:
                print(f"Error syncing guild: {guild_id}")

    async def setup(self):
        try:
            await self.add_cog(BasicCog(bot=self, channels=self.chat_channels))
            await self.add_cog(MusicCog(bot=self))
            #await self.add_cog(GambleCog(bot=self))
        except Exception as e:
                print(f"Setup failed: {e}")
        finally:
            print("Cogs Loaded!")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.sync_bot()
        for guild in self.guilds:
            self.voice_channel[guild.id] = None
        activity = discord.Activity(type=discord.ActivityType.watching, name="Your Every Move")
        await self.change_presence(status=discord.Status.online, activity=activity)

async def main(settings):
    bot = PotatoBot(command_prefix=settings['command_prefix'],
                    chat_channels=settings['chat_channels'],
                    guild_channels=settings['guild_channels'])
    await bot.setup()
    await bot.start(token)

if __name__ == "__main__":
    try:
        if not os.path.exists('downloads'):
            os.mkdir('downloads')
        if not os.path.exists('server_settings.json'):
            print("Discord Token:", arg_token)
            # If the file doesn't exist, create it and write the JSON data
            data = {
                "command_prefix": "!",
                "intents": "all",
                "chat_channels": [],
                "guild_channels": [],
                "token": arg_token,
            }
            with open('server_settings.json', 'w') as file:
                json.dump(data, file, indent=4)
                print('Settings file created, please alter as needed!')
        with open('server_settings.json', 'r') as file:
            settings = json.load(file)
    except Exception as e:
        print(f"Error loading settings: {e}")

    if arg_token and settings['token'] == "":
        print('No token found!')
        quit()
    if arg_token != settings['token'] and arg_token != "":
        settings['token'] = arg_token
        with open('server_settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
            print('Token updated')
    token = settings['token']
    asyncio.run(main(settings))
