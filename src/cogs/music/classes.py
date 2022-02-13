import copy

import wavelink

import asyncio
import async_timeout

from typing import Optional

from datetime import timedelta

import disnake
from disnake import Member
from disnake.ext import menus
from disnake.ext.commands import Context

class Track(wavelink.Track):
    __slots__ = ('requester', )
    
    def __init__(self, *args, **kwargs):
        super.__init__(*args)
        
        self.requester = kwargs.get('requester')

class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.context: Context = kwargs.get('context', None)
        if self.context:
            self.dj: Member = self.context.author
        
        #controller and queue
        self.controller = None
        self.queue = asyncio.Queue()
        
        #player status
        self.waiting = False
        self.updating = False
        
        #voting
        self.skip_votes = set()
        self.stop_votes = set()
        self.pause_votes = set()
        self.resume_votes = set()
        self.shuffle_votes = set()
        
    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return

        #clearing votes
        self.skip_votes.clear()
        self.stop_votes.clear()
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.shuffle_votes.clear()
        
        try:
            #setting watiting to true
            self.watiing = True
            
            #adding a timeout so it doesnt try forever
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            #Music hasnt been played for 5 minutes -> cleanup
            return await self.teardown()
        
        await self.play(track)
        self.waiting = False
        
        #invoking the controller
        await self.invoke_controller()
    
    async def invoke_controller(self) -> None:

        if self.updating:
            return 
        
        self.updating = True
        
        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.contoller.start(self.context)
        
        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except disnake.HTTPException:
                pass

            self.controller.stop()
            
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)
        
        else: 
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed = embed)
        
        self.updating = False

    def build_embed(self) -> Optional[disnake.Embed]:
        track = self.current
        if not track:
            return 
    
        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()
        
        embed = disnake.Embed(
            title=f"Music Player >> {channel.name}",
            description=f"Currently playing:\n**`track.title`**\n\n"
        )
        embed.set_thumbnail(url=track.thumb)
        
        embed.add_field(name="Duration", value=str(timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Queue Length', value=str(qsize))
        embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
        embed.add_field(name='Requested By', value=track.requester.mention)
        embed.add_field(name='DJ', value=self.dj.mention)
        embed.add_field(name='Video URL', value=f'[Click me!]({track.uri})')

        return embed
        
    async def is_position_fresh(self) -> bool:
        
        try:
            async for message in self.context.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True                  
        except (disnake.HTTPException, AttributeError):
            return False  
    
    async def teardown(self):
        
        try:
            await self.controller.message.delete()
        except disnake.HTTPException:
            pass
        
        self.controller.stop()
        
        try:
            await self.destroy()
        except KeyError:
            pass
        
class InteractiveController(disnake.ui.View):
    
    def __init__(self, *, embed: disnake.Embed, player: Player):
        super().__init__(timeout=None)
    
    def update_context(self, payload: disnake.RawReactionActionEvent):
        """Getting the context from the user who reacted"""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member
        
        return ctx
    
    def reaction_check(self, payload: disnake.RawReactionActionEvent):
        
        if not payload.member or payload.member.bot or payload.message_id != self.message.id or payload.member not in self.bot.get_channel(int(self.player.channel_id)).members or payload.event_type == "REACTION_REMOVE": return False
        
        return payload.emoji in self.buttons
    
    async def send_initial_message(self, ctx: Context, channel: disnake.TextChannel) -> disnake.Message:
        return await channel.send(embed=self.embed)
    
    @menus.button(emoji = "\u25B6")
    async def resume(self, payload: disnake.RawReactionActionEvent):
        ctx = self.update_context(payload)
        
        command = self.bot.get_command('resume')
        ctx.command = command
        
        await self.bot.invoke(ctx)
    
    @menus.button(emoji='\u23F8')
    async def pause_command(self, payload: disnake.RawReactionActionEvent):
        ctx = self.update_context(payload)
        
        command = self.bot.get_command('pause')
        ctx.command = command
        
        await self.bot.invoke(ctx)
        
    @menus.button(emoji='\u23F9')
    async def stop_command(self, payload: disnake.RawReactionActionEvent):
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
    def __init__(self, entries, *, per_page = 8) -> None:
        super().__init__(entries, per_page=per_page)
    
    async def format_page(self, menu: menus.Menu, page):
        embed = disnake.Embed(title='Next up', description="\n".join(f'`{index}. {title}`' for index, title in enumerate(page, 1)))

        return embed
    
    def is_paginating(self):
        
        return True