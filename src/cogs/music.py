import datetime
import itertools
from logging import exception
import re
import disnake
import humanize
import wavelink
import asyncio
from typing import Union
from wavelink import Player
from disnake.ext import commands
from disnake.ext.commands import Cog, Context

from ..bot import Jarvide

#coustom exception
class NotPlaying(exception):
    pass


class MusicController:
    
    def __init__(self, bot, guild_id):
        self.bot = bot,
        self.guild_id = guild_id,
        self.channel = None
        
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        
        self.volume = 40
        self.now_playing = None
        
        self.bot.create_task(self.controller_loop()
        )
    
    async def controller_loop(self):
        await self.bot.wait_until_ready()
        
        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)
        
        while True:
            if self.now_playing:
                await self.now_playing.delete()
                
            self.next.clear()
            
            song = await self.queue.get()
            await player.play(song)
            self.now_playing = await self.channel.send(
                embed=disnake.embed(
                    title = f"now playing: {song}",
                    description = f"Volume = {self.volume}"
                )
            )
            
            await self.next.wait()
        
class Music(
    Cog
):
    def __init__(self, bot = Jarvide) -> None:
        self.bot = bot
        self.controllers =  {}
        
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink= wavelink.Client(bot=self.bot)
            
        self.bot.create_task(self.start_nodes())
        
    async def start_nodes(self):
        await self.bot.wait_until_ready()
        
        #TODO: we need to move this to a self hosted node
        node = await self.bot.wavelink.initiate_node(
            host="lavalink.devin-dev.xyz",
            port=443,
            rest_uri="http://lavalink.devin-dev.xyz:443",
            password="lava123",
            identifier="jarvide",
            region="us_central"
        )

        node.set_hook(self.on_event_hook)
    
    async def on_event_hook(self, event):
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            self.get_controller(event.player).next.set()

    async def get_controller(self, value: Union[Context, Player]) -> MusicController:
        """gets the music controller for the guild

        Args:
            value (Union[Context, Player]): a union of both disnake's context and the player object from wavelink

        Returns:
            MusicController: it returns a music controller object
        """
        if isinstance(value, Context):
            guild_id = value.guild.id
        else:
            guild_id = value.guild_id
            
        try:
            controller = self.controllers[guild_id]
        except  KeyError:
            controller = MusicController(self.bot, guild_id)
            self.controller[guild_id] = controller
            
        return controller

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send("hey you cant play music in dms!")
            except disnake.HTTPException:
                pass
        if isinstance(error, NotPlaying):
            return await ctx.send(" Uh oh im not playing anything")
                
    @commands.command(name="connect")
    async def _connect(self, ctx, *, channel: disnake.VoiceChannel= None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = disnake.Embed(
                    title="No channel to join",
                    description="I couldnt find a channel to join: try joining a channel or specifying a channel"
                )
                await ctx.send(embed)
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f"Connecting to `{channel.name}`", delete_after=15)
        await player.connect(channel.id)
        
    @commands.command()
    async def play(self, ctx, *, query: str):
        RURL = re.compile('https?:\/\/(?:www\.)?.+')
        if not RURL.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(f'{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        track = tracks[0]

        controller = self.get_controller(ctx)
        await controller.queue.put(track)
        await ctx.send(f'Added {str(track)} to the queue.', delete_after=15)

    @commands.command()
    async def pause(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            raise NotPlaying

        await ctx.send('Pausing the song!', delete_after=15)
        await player.set_pause(True)

    @commands.command()
    async def resume(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send('I am not currently paused!', delete_after=15)

        await ctx.send('Resuming the player!', delete_after=15)
        await player.set_pause(False)

    @commands.command()
    async def skip(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_playing:
            raise NotPlaying

        await ctx.send('Skipping the song!', delete_after=15)
        await player.stop()

    @commands.command()
    async def volume(self, ctx, *, vol: int):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        vol = max(min(vol, 1000), 0)
        controller.volume = vol

        await ctx.send(f'Setting the player volume to `{vol}`')
        await player.set_volume(vol)

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    async def now_playing(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            raise NotPlaying

        controller = self.get_controller(ctx)
        await controller.now_playing.delete()

        controller.now_playing = await ctx.send(f'Now playing: `{player.current}`')

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        if not player.current or not controller.queue._queue:
            return await ctx.send('There are no songs currently in the queue.', delete_after=20)

        upcoming = list(itertools.islice(controller.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{str(song)}`**' for song in upcoming)
        embed = disnake.Embed(
            title=f'Upcoming - Next {len(upcoming)}',
            description=fmt
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'dc'])
    async def stop(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            await player.disconnect()
            return await ctx.send('There was no controller to stop.')

        await player.disconnect()
        await ctx.send('Disconnected player and killed controller.', delete_after=20)

    @commands.command()
    async def info(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
              f'`{node.stats.players}` players are distributed on server.\n' \
              f'`{node.stats.playing_players}` players are playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}`\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)