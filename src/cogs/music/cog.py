import math
import disnake
import wavelink
from disnake.ext import commands

from src.bot import Jarvide
from .classes import Player
from .errors import IncorrectChannelError, NoChannelProvided

class Music(
    commands.Cog,
    wavelink.wavelinkMixin
):
    def __init__(self, bot: commands.Bot):
       self.bot = bot
       
       if not hasattr(bot, 'wavelink'):
           bot.wavelink = wavelink.Client(bot=bot)
       
       bot.loop.create_task(self.connect_nodes())
       
    async def connect_nodes(self) -> None:
        """Connect nodes to wavelink"""
        await self.bot.wait_until_ready()
        #TODO: make a private node
        await wavelink.NodePool.create_node(
            bot = self.bot,
            host = "localhost",
            port = 2333,
            password = "youshallnotpass",
            identifier="Main-Node"
        )
    
    
    @wavelink.WavelinkMixin.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        """Wavelink on ready event"""
        await self.bot.error_channel.send(
                f"```yaml\nNode<{node.identifier}> is on; standing by.\n```"
        )
    
    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        await payload.player.do_next()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if member.bot:
            return

        player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)
        
        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return
        
        channel = self.bot.get_channel(int(player.channel.id))
        
        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot:
                    continue
                else:
                    player.dj = m
                    return 
        
        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member
    
    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            
            return await ctx.send(embed= disnake.Embed(title="You must be in a vc or provide a vc! <a:error:942466910811983903>"))
        
    async def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        
        player: Player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        if player.context and player.context.channel != ctx.channel:
                await ctx.send(f'{ctx.author.mention}, you must be in {player.context.channel.mention} for this session.')
                raise IncorrectChannelError

        if ctx.command.name == 'connect' and not player.context or self.is_privileged(ctx):
            return
        

        if not player.channel_id:
            return

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return

        if player.is_connected and ctx.author not in channel.members:
                await ctx.send(f'{ctx.author.mention}, you must be in `{channel.name}` to use voice commands.')
                raise IncorrectChannelError
    
    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == 'stop' and len(channel.members) == 3:
            required = 2

        return required

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        return player.dj == ctx.author or ctx.author.guild_permissions.kick_members

    @commands.command()
    async def connect(self, ctx: commands.Context, *, channel: typing.Union[discord.VoiceChannel, discord.StageChannel] = None):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_connected:
            return

        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            raise NoChannelProvided

        await player.connect(channel.id)
        
def setup(bot: Jarvide) -> None:
    bot.add_cog(Music(bot))
    