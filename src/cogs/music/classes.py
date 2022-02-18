import asyncio
import copy
import datetime
import typing

import async_timeout
import disnake
import wavelink
from disnake.ext import commands, menus
from disnake.ui import View, button


class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ("requester", "thumbnail")

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get("requester")
        self.thumbail = kwargs.get("thumbnail")


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

    async def next(self) -> None:
        if self.waiting or self.updating:
            return

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            return await self.teardown()
        await self.play(track)
        self.waiting = False

        await self.invoke_controller()

    async def invoke_controller(self) -> None:
        if self.waiting:
            return

        self.updating = True

        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.send_initial_message(self.ctx, self.ctx.channel)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except disnake.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.send_initial_message(self.ctx, self.ctx.channel)

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

        embed = disnake.Embed(title=f"Music Controller | {channel.name}")
        embed.description = f"Now Playing:\n**[{track.title}]({track.uri})**\n\n"
        try:
            embed.set_thumbnail(url=track.thumb)
        except AttributeError:
            pass

        duration = str(datetime.timedelta(seconds=int(track.length)))
        position = str(datetime.timedelta(seconds=int(self.position)))

        if duration.startswith("0:"):
            duration = duration.replace("0:", "")
        if position.startswith("0:"):
            position = position.replace("0:", "")

        embed.add_field(name="Duration", value=f"{position}/{duration}")
        embed.add_field(name="Queue Length", value=str(self.queue.qsize()))
        embed.add_field(name="Volume", value=f"**`{self.volume}%`**")
        embed.add_field(name="Requested By", value=track.requester.mention)
        embed.add_field(name="DJ", value=self.dj.mention)

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
        except (disnake.HTTPException, AttributeError):
            pass

        self.controller.stop()
        await self.disconnect()


class InteractiveController(View):
    """The Players interactive controller menu class."""

    def __init__(self, *, embed: disnake.Embed, player: Player):
        super().__init__(timeout=None)
        self.embed = embed
        self.player = player

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.author.bot:
            return False
        if interaction.author not in self.player.channel.members:
            return False
        return True

    async def send_initial_message(self, ctx: commands.Context, channel: disnake.TextChannel) -> disnake.Message:
        self.message = await channel.send(embed=self.embed, view=self)

    @button(emoji="\u25B6")
    async def resume_command(self, button: button, interaction: disnake.MessageInteraction):
        """Resume button."""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("resume")
        await interaction.bot.invoke(ctx)

    @button(emoji="\u23F8")
    async def pause_command(self, button: button, interaction: disnake.MessageInteraction):
        """Pause button"""
        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("pause")
        await interaction.bot.invoke(ctx)

    @button(emoji="\u23F9")
    async def stop_command(self, button: button, interaction: disnake.MessageInteraction):
        """Stop button."""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("stop")
        await interaction.bot.invoke(ctx)

    @button(emoji="\u23ED")
    async def skip_command(self, button: button, interaction: disnake.MessageInteraction):
        """Skip button."""
        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("skip")
        await interaction.bot.invoke(ctx)

    @button(emoji="\U0001F500")
    async def shuffle_command(self, button: button, interaction: disnake.MessageInteraction):
        """Shuffle button."""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("shuffle")
        await interaction.bot.invoke(ctx)

    @button(emoji="\u2795")
    async def volup_command(self, button: button, interaction: disnake.MessageInteraction):
        """Volume up button"""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("vol_up")
        await interaction.bot.invoke(ctx)

    @button(emoji="\u2796")
    async def voldown_command(self, button: button, interaction: disnake.MessageInteraction):
        """Volume down button."""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("vol_down")
        await interaction.bot.invoke(ctx)

    @button(label="Queue", emoji="\U0001F1F6")
    async def queue_command(self, button: button, interaction: disnake.MessageInteraction):
        """Player queue button."""

        ctx = await interaction.bot.get_context(interaction.message)
        ctx.command = interaction.bot.get_command("queue")
        await interaction.bot.invoke(ctx)


class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=8):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = disnake.Embed(title="Next up")
        embed.description = "\n".join(f"**{index}.** {title}" for index, title in enumerate(page, 1))

        return embed

    def is_paginating(self):
        return True
