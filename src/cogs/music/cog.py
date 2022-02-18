
import datetime
import re

import math
import random
import typing
import disnake
import wavelink


from disnake.ext import menus
from disnake.ext import commands

from src.bot import Jarvide
from .errors import IncorrectChannelError, NoChannelProvided
from .classes import PaginatorSource, Player, Track



YOUTUBE_URL = re.compile(r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?‌​=]*)?')
SOUNDCLOUD_URL = re.compile(r'http(?:s?):\/\/(?:www\.)?(m\.)?(soundcloud\.com|snd\.sc)\/(.*)\/(.*)')


class Music(
    commands.Cog
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = "🎹"
        self.short_help_doc = "Music music commands"
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self) -> None:
        """Connect nodes to wavelink"""
        await self.bot.wait_until_ready()
        # TODO: make a private node
        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="localhost",
            port=2333,
            password="youshallnotpass",
            identifier="Main-Node"
        )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        """Wavelink on ready event"""
        await self.bot.error_channel.send(
            f"```yaml\nNode<{node.identifier}> is on; standing by.\n```"
        )
    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, error):
        await player.next()
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player, track, threshold):
        await player.next()
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        await player.next()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before, after):
        if member.bot: return

        player = wavelink.NodePool.get_node().get_player(member.guild)
        
        if not player: return
        
        if not player.channel or not player.ctx:
            wavelink.NodePool.get_node().players.pop(member.guild.id); return;
        
        channel = player.channel
        
        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot: continue;
                else: player.dj = m; return;
        
        elif after.channel == channel and player.dj not in channel.members: player.dj = member
    
    
    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx:commands.Context):
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        
        if player and player.ctx and player.ctx.channel != ctx.channel:
            await ctx.send(f"Hey {ctx.author.mention}!, you must be in {player.ctx.channel.mention}!")
            raise IncorrectChannelError("yes")

        
        if player and player.channel and ctx.author not in player.channel.members:
            await ctx.send(f"Hey {ctx.author.mention}!, you must be in `{player.channel.name}`!")
            raise IncorrectChannelError
    
        if ctx.command.name == 'connect' and not player or self.is_privileged(ctx):
            return
        
        if player and not player.channel:
            return
        
            
    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == 'stop' and len(channel.members) == 3:
            required = 2

        return required
    
    @commands.command()
    async def connect(self, ctx: commands.Context, *, channel: disnake.VoiceChannel= None):
        """ connects either the channel that the user is in or the channel provided """
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        
        if player:
            await ctx.send(embed= disnake.Embed(
                title="The bot has already been connected to a vc! disconnect it first!"
            ))
            return
        
        embed = disnake.Embed(
            title="Trying to connect <a:loading_grey:942386360877219881>"
        )
        message = await ctx.send(embed=embed)
        
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            await message.edit(embed= disnake.Embed(title="no channels found"))
            return 
        
        player  = Player(ctx=ctx)
        vc: Player = await channel.connect(cls=player)
        await message.edit(embed=disnake.Embed(title="🎵 connected. Have fun! ✅"), delete_after=15)
        return vc
    
    #TODO: instead of a union make use of RE
    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: typing.Union[wavelink.SoundCloudTrack, wavelink.YouTubeMusicTrack, wavelink.YouTubeTrack, wavelink.YouTubePlaylist]):
        """ Plays a song that matches the query. supported platforms: `Soundcloud`, `YouTube`, `Youtube-Music`, `Youtube-Playlist` """
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        print(player)
        if not player or not player.is_connected():
            player: Player = await self.connect(ctx)
            if not player:
                return
        
        if not query:
            await ctx.send(embed=disnake.Embed(title="Not a vaild query!!!"))
        
        if isinstance(query, wavelink.YouTubePlaylist):
            for track in query.tracks:
                track = Track(track.id, track.info, requester=ctx.author)
                await player.queue.put(track)
            
        
            
            #TODO: make it an embed
            await ctx.send("added tracks")
        
        else: 
            track = Track(query.id, query.info, requester=ctx.author)
            await ctx.send(f"added song {track.title}")
            await player.queue.put(track)
        
        
        if not player.is_playing():
            await player.next()
    
    @commands.command()
    async def pause(self, ctx: commands.Context):
        """ Pauses the current player """
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        
        if not player:
            return
        
        if player.is_paused or not player.is_connected:
            return
        
        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send('Vote to pause passed. Pausing player.', delete_after=10)
            player.pause_votes.clear()
            await player.set_pause(True)
        else:
            await ctx.send(f'{ctx.author.mention} has voted to pause the player.', delete_after=15)
            
    @commands.command()
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send('An admin or DJ has resumed the player.', delete_after=10)
            player.resume_votes.clear()

            return await player.set_pause(False)

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send('Vote to resume passed. Resuming player.', delete_after=10)
            player.resume_votes.clear()
            await player.set_pause(False)
        else:
            await ctx.send(f'{ctx.author.mention} has voted to resume the player.', delete_after=15)

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if not player:
            return
        
        return player.dj == ctx.author or ctx.author.guild_permissions.kick_members
    
    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send('An admin or DJ has skipped the song.', delete_after=10)
            player.skip_votes.clear()

            return await player.next()

        if ctx.author == player.current.requester:
            await ctx.send('The song requester has skipped the song.', delete_after=10)
            player.skip_votes.clear()

            return await player.next()

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send('Vote to skip passed. Skipping song.', delete_after=10)
            player.skip_votes.clear()
            await player.next()
        else:
            await ctx.send(f'{ctx.author.mention} has voted to skip the song.', delete_after=15)

    @commands.command(aliases=["leave", "gtfo", "dc", "disconnect"])
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send('An admin or DJ has stopped the player.', delete_after=10)
            return await player.teardown()

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send('Vote to stop passed. Stopping the player.', delete_after=10)
            await player.teardown()
        else:
            await ctx.send(f'{ctx.author.mention} has voted to stop the player.', delete_after=15)

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            return await ctx.send('Only the DJ or admins may change the volume.')

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        await player.set_volume(vol)
        await ctx.send(f'Set the volume to **{vol}**%', delete_after=7)

    @commands.command(aliases=['mix'])
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            return await ctx.send('Add more songs to the queue before shuffling.', delete_after=15)

        if self.is_privileged(ctx):
            await ctx.send('An admin or DJ has shuffled the playlist.', delete_after=10)
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send('Vote to shuffle passed. Shuffling the playlist.', delete_after=10)
            player.shuffle_votes.clear()
            random.shuffle(player.queue._queue)
        else:
            await ctx.send(f'{ctx.author.mention} has voted to shuffle the playlist.', delete_after=15)

    @commands.command(hidden=True)
    async def vol_up(self, ctx: commands.Context):
        """Command used for volume up button."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected or not self.is_privileged(ctx):
            return

        vol = int(math.ceil((player.volume + 10) / 10)) * 10

        if vol > 100:
            vol = 100
            await ctx.send('Maximum volume reached', delete_after=7)

        await player.set_volume(vol)

    @commands.command(hidden=True)
    async def vol_down(self, ctx: commands.Context):
        """Command used for volume down button."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected or not self.is_privileged(ctx):
            return

        vol = int(math.ceil((player.volume - 10) / 10)) * 10

        if vol < 0:
            vol = 0
            await ctx.send('Player is currently muted', delete_after=10)

        await player.set_volume(vol)

    @commands.command(aliases=['eq'])
    async def equalizer(self, ctx: commands.Context, *, equalizer: str):
        """Change the players equalizer."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            return await ctx.send('Only the DJ or admins may change the equalizer.')

        eqs = {'flat': wavelink.Equalizer.flat(),
               'boost': wavelink.Equalizer.boost(),
               'metal': wavelink.Equalizer.metal(),
               'piano': wavelink.Equalizer.piano()}

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = "\n".join(eqs.keys())
            return await ctx.send(f'Invalid EQ provided. Valid EQs:\n\n{joined}')

        await ctx.send(f'Successfully changed equalizer to {equalizer}', delete_after=15)
        await player.set_eq(eq)

    @commands.command(aliases=['q', 'que'])
    async def queue(self, ctx: commands.Context):
        """Display the players queued songs."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if player.queue.qsize() == 0:
            return await ctx.send('There are no more songs in the queue.', delete_after=15)

        entries = ["".join(f"[{track.title}]({track.uri})" for track in player.queue._queue)]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(source=pages, timeout=None)

        await paginator.start(ctx)
    @commands.command()
    async def seek(self, ctx, seconds:int):
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        
        if not player.is_connected:
            return
        try:
            embed = disnake.Embed(title="Seeking")
            await player.seek(int(seconds * 1000))
            embed.add_field(name=f"seeked to {datetime.timedelta(milliseconds=int(player.position))}",value=f" skipped to {seconds}")
            
            await ctx.reply(embed=embed)
        except:
            pass #TODO: FIGURE OUT EXCEPTION
    @commands.command(aliases=['np', 'now_playing', 'current'])
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        await player.invoke_controller()

    @commands.command(aliases=['swap'])
    async def swap_dj(self, ctx: commands.Context, *, member: disnake.Member = None):
        """Swap the current DJ to another member in the voice channel."""
        player: Player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if not player:
            return
        
        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            return await ctx.send('Only admins and the DJ may use this command.', delete_after=15)

        members = self.bot.get_channel(int(player.channel_id)).members

        if member and member not in members:
            return await ctx.send(f'{member} is not currently in voice, so can not be a DJ.', delete_after=15)

        if member and member == player.dj:
            return await ctx.send('Cannot swap DJ to the current DJ... :)', delete_after=15)

        if len(members) <= 2:
            return await ctx.send('No more members to swap to.', delete_after=15)

        if member:
            player.dj = member
            return await ctx.send(f'{member.mention} is now the DJ.')

        for m in members:
            if m == player.dj or m.bot:
                continue
            else:
                player.dj = m
                return await ctx.send(f'{member.mention} is now the DJ.')
def setup(bot: Jarvide) -> None:
    bot.add_cog(Music(bot))
