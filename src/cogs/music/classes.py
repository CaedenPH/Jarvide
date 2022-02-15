import copy

import asyncio
import datetime
import typing
import async_timeout

import wavelink

import disnake
from disnake.ext import commands
from disnake.ext import menus

class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ('requester', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')

class Player(wavelink.Player):
    """a player with a queue"""

    def __init__(self, ctx):
        super().__init__()
        self.ctx: commands.Context = ctx
        self.dj: disnake.Member = self.ctx.author
        
        self.queue = asyncio.Queue()
        self.controller = None
        
        self.waiting = False
        self.updating = False

        
        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()
        
    async def next(self)-> None:
        if self.waiting or self.updating:
            return

        # Clear the votes for a new song...
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        
        try:
            self.waiting = True 
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            return await self.teardown()
        await self.play(track)
        self.waiting = False
        
        await self.invoke_controller()
        
    async def invoke_controller(self)-> None:
        if self.waiting:
            return
        
        self.updating = True
        
        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.ctx)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except disnake.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.ctx)

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False
    
    def build_embed(self) -> typing.Optional[disnake.Embed]:
        """Method which builds our players controller embed."""
        track = self.track
        if not track:
            return

        channel = self.channel

        embed = disnake.Embed(title=f'Music Controller | {channel.name}')
        embed.description = f'Now Playing:\n**`{track.title}`**\n\n'
        try:
            embed.set_thumbnail(url=track.thumb)
        except AttributeError:
            pass

        embed.add_field(name='Duration', value=str(datetime.timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Queue Length', value=str(self.queue.qsize()))
        embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
        embed.add_field(name='Requested By', value=track.requester.mention)
        embed.add_field(name='DJ', value=self.dj.mention)
        embed.add_field(name='Video URL', value=f'[Click Here!]({track.uri})')

        return embed
    
    async def is_position_fresh(self) -> bool:
        """Method which checks whether the player controller should be remade or updated."""
        try:
            async for message in self.ctx.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True
        except (disnake.HTTPException, AttributeError):
            return False

        return False

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        try:
            await self.controller.message.delete()
        except disnake.HTTPException:
            pass

        self.controller.stop()
        await self.disconnect()

class InteractiveController(menus.Menu):
    """The Players interactive controller menu class."""

    def __init__(self, *, embed: disnake.Embed, player: Player):
        super().__init__(timeout=None)

        self.embed = embed
        self.player = player

    def update_context(self, payload: disnake.RawReactionActionEvent):
        """Update our context with the user who reacted."""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member

        return ctx

    def reaction_check(self, payload: disnake.RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False

        if not payload.member:
            return False
        if payload.member.bot:
            return False
        if payload.message_id != self.message.id:
            return False
        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: disnake.TextChannel) -> disnake.Message:
        return await channel.send(embed=self.embed)

    @menus.button(emoji='\u25B6')
    async def resume_command(self, payload: disnake.RawReactionActionEvent):
        """Resume button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('resume')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F8')
    async def pause_command(self, payload: disnake.RawReactionActionEvent):
        """Pause button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('pause')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F9')
    async def stop_command(self, payload: disnake.RawReactionActionEvent):
        """Stop button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('stop')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23ED')
    async def skip_command(self, payload: disnake.RawReactionActionEvent):
        """Skip button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('skip')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F500')
    async def shuffle_command(self, payload: disnake.RawReactionActionEvent):
        """Shuffle button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('shuffle')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2795')
    async def volup_command(self, payload: disnake.RawReactionActionEvent):
        """Volume up button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_up')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2796')
    async def voldown_command(self, payload: disnake.RawReactionActionEvent):
        """Volume down button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_down')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F1F6')
    async def queue_command(self, payload: disnake.RawReactionActionEvent):
        """Player queue button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('queue')
        ctx.command = command

        await self.bot.invoke(ctx)


class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=8):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = disnake.Embed(title='Next up')
        embed.description = '\n'.join(f'`{index}. {title}`' for index, title in enumerate(page, 1))

        return embed

    def is_paginating(self):
        return True