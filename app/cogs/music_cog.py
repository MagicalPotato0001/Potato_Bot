import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from youtubesearchpython import VideosSearch
import yt_dlp as youtube_dl
import os
import asyncio
import random

class SkipButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.red, label="Skip", emoji="⏭️")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.cog.bot.voice_channel[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if len(self.cog.music_queue[interaction.guild_id]) > 0:
            self.cog.is_playing[interaction.guild_id] = True
            self.cog.is_paused[interaction.guild_id] = False
            self.cog.bot.voice_channel[interaction.guild_id].stop()
            self.cog.play_next(interaction)
        elif self.cog.is_playing[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            self.cog.bot.voice_channel[interaction.guild_id].stop()
            self.cog.play_next(interaction)
        else:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            await interaction.followup.send(f"{interaction.user.mention} No songs left in queue!")

class ClearButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.red, label="Clear", emoji="🗑️")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.cog.bot.voice_channel[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if self.cog.is_playing[interaction.guild_id]:
            self.cog.bot.voice_channel[interaction.guild_id].stop()
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
        self.cog.music_queue[interaction.guild_id] = []

class LeaveButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.grey, label="Leave", emoji="❌")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.cog.bot.voice_channel[interaction.guild_id]:
            await self.cog.bot.voice_channel[interaction.guild_id].disconnect()
            self.cog.bot.voice_channel[interaction.guild_id] = None
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            self.cog.reset_inactivity_timer(interaction)
        else:
            await interaction.followup.send("I'm not in a voice channel.")

class ShuffleButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.green, label="Shuffle", emoji="🔀")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if len(self.cog.music_queue[interaction.guild_id]) > 1:
            random.shuffle(self.cog.music_queue[interaction.guild_id])
        else:
            await interaction.followup.send(f"{interaction.user.mention} Video queue not large enough!")

class VolumeUpButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.green, label="Volume Up", emoji="🔊")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        self.cog.bot.voice_channel[interaction.guild_id].source = discord.PCMVolumeTransformer(self.cog.bot.voice_channel[interaction.guild_id].source, volume=1.25)
        await interaction.response.defer()

class VolumeDownButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.green, label="Volume Down", emoji="🔉")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        self.cog.bot.voice_channel[interaction.guild_id].source = discord.PCMVolumeTransformer(self.cog.bot.voice_channel[interaction.guild_id].source, volume=0.75)
        await interaction.response.defer()

class PauseButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.primary, label="Pause", emoji="⏸️")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.cog.bot.voice_channel[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if self.cog.is_playing[interaction.guild_id] and not self.cog.is_paused[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = True
            self.cog.bot.voice_channel[interaction.guild_id].pause()
            self.cog.start_inactivity_timer(interaction)
        elif not self.cog.is_playing[interaction.guild_id] and not self.cog.is_paused[interaction.guild_id]:
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not currently playing a video!")
        else:
            await interaction.followup.send(f"{interaction.user.mention} Video is already paused!")

class ResumeButton(Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.primary, label="Resume", emoji="▶️")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.cog.bot.voice_channel[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = False
            self.cog.is_paused[interaction.guild_id] = False
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if not self.cog.is_playing[interaction.guild_id] and self.cog.is_paused[interaction.guild_id]:
            self.cog.is_playing[interaction.guild_id] = True
            self.cog.is_paused[interaction.guild_id] = False
            self.cog.bot.voice_channel[interaction.guild_id].resume()
            self.cog.reset_inactivity_timer(interaction)
        elif not self.cog.is_playing[interaction.guild_id] and not self.cog.is_paused[interaction.guild_id]:
            await interaction.followup.send(f"{interaction.user.mention} Potato Player is not currently playing a video!")
        else:
            await interaction.followup.send(f"{interaction.user.mention} Video is already playing!")

class ControlView(View):
    def __init__(self, music_cog):
        super().__init__()
        self.add_item(SkipButton(music_cog))
        self.add_item(ClearButton(music_cog))
        self.add_item(PauseButton(music_cog))
        self.add_item(ResumeButton(music_cog))
        self.add_item(ShuffleButton(music_cog))
        self.add_item(LeaveButton(music_cog))



class MusicCog(commands.Cog):
    def __init__(self,
                 bot = None,
                 verbose = True,
                 name = "Potato Bot",
                 ytdl_options = {},
                 ffmpeg_options = {},
                 max_queue = 15):
        self.bot = bot
        self.verbose = verbose
        self.name = name
        self.is_playing = {}
        self.is_paused = {}
        self.music_queue = {}
        self.max_q = max_queue
        self.inactivity_timer = {}
        self.current_channel = {}
        self.volume = 1.0

        if ytdl_options:
            self.ytdl = ytdl_options
        else:
            self.ytdl = {
                'format': 'bestaudio/best',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'outtmpl':"downloads" + '/%(id)s.%(ext)s',
            }
        
        if ffmpeg_options:
            self.FFMPEG = ffmpeg_options
        else:
            self.FFMPEG = {
                'options': '-vn',
            }

    def start_inactivity_timer(self, interaction: discord.Interaction):
        if self.inactivity_timer[interaction.guild_id]:
            self.inactivity_timer[interaction.guild_id].cancel()
        
        self.inactivity_timer[interaction.guild_id] = self.bot.loop.create_task(self.disconnect_on_inactivity(interaction))

    async def disconnect_on_inactivity(self, interaction: discord.Interaction):
        await asyncio.sleep(15 * 60)  # 15 minutes
        if not self.is_playing[interaction.guild_id] and self.bot.voice_channel[interaction.guild_id]:
            await self.bot.voice_channel[interaction.guild_id].disconnect()
            self.bot.voice_channel[interaction.guild_id] = None
    
    def reset_inactivity_timer(self, interaction: discord.Interaction):
        if self.inactivity_timer[interaction.guild_id]:
            self.inactivity_timer[interaction.guild_id].cancel()
            self.inactivity_timer[interaction.guild_id] = None

    async def search_youtube(self, query):
        videos_search = VideosSearch(query, limit=5)
        search_results = videos_search.result()

        video_list = [(video['title'], video['link']) for video in search_results['result']]
        
        return video_list

    async def autocomplete_youtube(self, interaction: discord.Interaction, current: str):
        if not current:
            return []
        results = await self.search_youtube(current)
        return [app_commands.Choice(name=video_title, value=video_url) for video_title, video_url in results]
    
    def get_download_path(self, youtube_id):
        return os.path.join('downloads/', f"{youtube_id}.mp3")
    
    def play_next(self, interaction: discord.Interaction):
        if len(self.music_queue[interaction.guild_id]) > 0:
            next_video = self.music_queue[interaction.guild_id].pop(0)
            download_path = next_video.get('download_path')
            title = next_video.get('title')
            url = next_video.get('url')
            requested = next_video.get('requested')
            y_id = next_video.get('y_id')

            embed = discord.Embed(title="🎶 Now Playing", color=discord.Color.blue())
            embed.add_field(name="Title", value=title, inline=False)
            embed.add_field(name="URL", value=url, inline=False)
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{y_id}/0.jpg")
            embed.set_footer(text=f"Requested by {requested}", icon_url=self.bot.user.avatar.url)

            if self.current_channel[interaction.guild_id]:
                self.bot.loop.create_task(self.current_channel[interaction.guild_id].send(embed=embed, view=ControlView(self)))
            self.bot.voice_channel[interaction.guild_id].play(discord.FFmpegPCMAudio(source=download_path, **self.FFMPEG), after=lambda e: self.play_next(interaction))
            self.is_playing[interaction.guild_id] = True
        else:
            self.is_playing[interaction.guild_id] = False
            self.start_inactivity_timer(interaction)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.is_playing[guild.id] = False
            self.is_paused[guild.id] = False
            self.music_queue[guild.id] = []
            self.inactivity_timer[guild.id] = None
            self.current_channel[guild.id] = None
        print("[MusicCog] Loaded")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            guild_id = member.guild.id
            if before.channel is not None and after.channel is None:
                self.bot.voice_channel[guild_id] = None
                self.is_playing[guild_id] = False
                self.is_paused[guild_id] = False
                return
            if after.channel is not None:
                if self.is_playing[guild_id] and not self.is_paused[guild_id]:
                    self.is_playing[guild_id] = False
                    self.is_paused[guild_id] = True

    @app_commands.command(name="join", description="Join users voice channel!")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            self.bot.voice_channel[interaction.guild_id] = await interaction.user.voice.channel.connect()
            await interaction.response.send_message(f"Joined {interaction.user.voice.channel.name} channel.")
            self.start_inactivity_timer(interaction)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} needs to be in a voice channel!")

    @app_commands.command(name="leave", description="Leave the voice channel!")
    async def leave(self, interaction: discord.Interaction):
        if self.bot.voice_channel[interaction.guild_id]:
            await self.bot.voice_channel[interaction.guild_id].disconnect()
            self.bot.voice_channel[interaction.guild_id] = None
            await interaction.response.send_message("Left the voice channel.")
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            self.reset_inactivity_timer(interaction)
        else:
            await interaction.response.send_message("I'm not in a voice channel.")

    @app_commands.command(name="play", description="Play a youtube video!")
    @app_commands.autocomplete(url=autocomplete_youtube)
    async def play(self, interaction: discord.Interaction, url: str):
        try:
            if not self.bot.voice_channel[interaction.guild_id]:
                if interaction.user.voice and interaction.user.voice.channel:
                    self.bot.voice_channel[interaction.guild_id] = await interaction.user.voice.channel.connect()
                else:
                    await interaction.response.send_message(f"{interaction.user.mention} needs to be in a voice channel!")
                    return
            await interaction.response.defer()
            self.current_channel[interaction.guild_id] = interaction.channel
            with youtube_dl.YoutubeDL(self.ytdl) as ytdl:
                info = ytdl.extract_info(url, download=False)
                youtube_id = info.get("id", None)
                youtube_title = info.get("title", None)
                download_path = self.get_download_path(youtube_id)

                if not os.path.exists(download_path):
                    ytdl.download([url])
                    print(f"Downloaded and saved to {download_path}")
            video_info = {
                'download_path': download_path,
                'title': youtube_title,
                'url': url,
                'requested': interaction.user.display_name,
                'y_id': youtube_id
            }
            if self.is_playing[interaction.guild_id]:
                self.music_queue[interaction.guild_id].append(video_info)
            else:
                self.music_queue[interaction.guild_id].insert(0, video_info)
                self.play_next(interaction)
            self.reset_inactivity_timer(interaction)
            await interaction.followup.send(f"{youtube_title} Requested!")
        except Exception as e:
            print(f"Error playing video: {e}")
            await interaction.followup.send(f"{interaction.user.mention} Error playing video!")

    @app_commands.command(name="pause", description="Pause the current video!")
    async def pause(self, interaction: discord.Interaction):
        if not self.bot.voice_channel[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if self.is_playing[interaction.guild_id] and not self.is_paused[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = True
            self.bot.voice_channel[interaction.guild_id].pause()
            await interaction.response.send_message(f"{interaction.user.mention} Video paused!")
            self.start_inactivity_timer(interaction)
        elif not self.is_playing[interaction.guild_id] and not self.is_paused[interaction.guild_id]:
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not currently playing a video!")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Video is already paused!")

    @app_commands.command(name="resume", description="Resume the current video!")
    async def resume(self, interaction: discord.Interaction):
        if not self.bot.voice_channel[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if not self.is_playing[interaction.guild_id] and self.is_paused[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = True
            self.is_paused[interaction.guild_id] = False
            self.bot.voice_channel[interaction.guild_id].resume()
            await interaction.response.send_message(f"{interaction.user.mention} Video resumed!")
            self.reset_inactivity_timer(interaction)
        elif not self.is_playing[interaction.guild_id] and not self.is_paused[interaction.guild_id]:
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not currently playing a video!")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Video is already playing!")

    
    @app_commands.command(name="skip", description="Skip the current video!")
    async def skip(self, interaction: discord.Interaction):
        if not self.bot.voice_channel[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if len(self.music_queue[interaction.guild_id]) > 0:
            self.is_playing[interaction.guild_id] = True
            self.is_paused[interaction.guild_id] = False
            self.bot.voice_channel[interaction.guild_id].stop()
            await interaction.response.send_message(f"{interaction.user.mention} Song skipped!")
            self.play_next(interaction)
        elif self.is_playing[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            self.bot.voice_channel[interaction.guild_id].stop()
            await interaction.response.send_message(f"{interaction.user.mention} Song skipped!")
            self.play_next(interaction)
        else:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            await interaction.response.send_message(f"{interaction.user.mention} No songs left in queue!")

    @app_commands.command(name="queue", description="Queue a youtube video!")
    @app_commands.autocomplete(url=autocomplete_youtube)
    async def queue(self, interaction: discord.Interaction, url: str):
        try:
            if not len(self.music_queue[interaction.guild_id]) <= self.max_q:
                await interaction.response.send_message(f"{interaction.user.mention} Queue limit reached!")
                return
            if not self.bot.voice_channel[interaction.guild_id]:
                self.is_playing[interaction.guild_id] == False
                self.is_paused[interaction.guild_id] == False
                if interaction.user.voice and interaction.user.voice.channel:
                    self.bot.voice_channel[interaction.guild_id] = await interaction.user.voice.channel.connect()
                else:
                    await interaction.response.send_message(f"{interaction.user.mention} needs to be in a voice channel!")
                    return
            await interaction.response.defer()
            self.current_channel[interaction.guild_id] = interaction.channel
            with youtube_dl.YoutubeDL(self.ytdl) as ytdl:
                    info = ytdl.extract_info(url, download=False)
                    youtube_id = info.get("id", None)
                    youtube_title = info.get("title", None)
                    download_path = self.get_download_path(youtube_id)

                    if not os.path.exists(download_path):
                        ytdl.download([url])
                        print(f"Downloaded and saved to {download_path}")
            video_info = {
                    'download_path': download_path,
                    'title': youtube_title,
                    'url': url,
                    'requested': interaction.user.display_name,
                    'y_id': youtube_id
            }
            self.music_queue[interaction.guild_id].append(video_info)
            if not self.is_playing[interaction.guild_id]:
                self.play_next(interaction)
            self.reset_inactivity_timer(interaction)
            await interaction.followup.send(f"{interaction.user.mention} {youtube_title} queued!\n {url}")
        except Exception as e:
            print(f"Error queueing video: {e}")
            await interaction.followup.send(f"{interaction.user.mention} Error queueing video!")
        

    @app_commands.command(name="clear", description="Clear the video queue!")
    async def clear(self, interaction: discord.Interaction):
        if not self.bot.voice_channel[interaction.guild_id]:
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
            await interaction.response.send_message(f"{interaction.user.mention} Potato Player is not in a voice channel!")
            return
        if self.is_playing[interaction.guild_id]:
            self.bot.voice_channel[interaction.guild_id].stop()
            self.is_playing[interaction.guild_id] = False
            self.is_paused[interaction.guild_id] = False
        self.music_queue[interaction.guild_id] = []
        await interaction.response.send_message(f"{interaction.user.mention} Video queue cleared!")

    @app_commands.command(name="shuffle", description="Shuffle the video queue!")
    async def shuffle(self, interaction: discord.Interaction):
        if len(self.music_queue[interaction.guild_id]) > 1:
            random.shuffle(self.music_queue[interaction.guild_id])
            await interaction.response.send_message(f"{interaction.user.mention} Video queue shuffled!")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Video queue not large enough!")