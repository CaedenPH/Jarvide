from __future__ import annotations

import aiohttp
import disnake
import io
import random

from disnake.ext import commands
from typing import TypeVar, Type

j = "<:j:929451908354174996>"
a = "<:a:929451929577328640>"
r = "<:r:929451948715945984>"
v = "<:v:929451995302096996>"
i = "<:i:929452020245606430>"
d = "<:d:929452037362552923>"
e = "<:e_:929452059483328592>"


def add_lines(content: str) -> list[str]:
    enumerated = list(enumerate(content.split("\n"), 1))
    lines = []
    for number, line in enumerated:
        number = ("0" * (len(str(enumerated[-1][0])) - len(str(number)))) + str(number)
        line = f"\n{number} | {line}"
        lines.append(line)

    return lines


Self = TypeVar("Self")


class IncorrectInstance(Exception):
    """User passed incorrect instance"""

    def __init__(self, argument: str) -> None:
        super().__init__(f"{argument}")


class File:
    def __init__(self, *, filename, content, bot) -> None:
        self.filename = filename
        self.bot = bot
        self.content = content
        self.undo = []  # passed in EditView
        self.redo = []  # this too
        self.version_history = {}
        self.setup()
        self.extension = self.filename.split(".")[-1]

    def setup(self) -> None:
        if hasattr(self.filename, "content"):
            self.filename = self.filename.content
        if hasattr(self.content, "content"):
            self.content = self.content.content
        if hasattr(self.content, "decode"):
            self.content = self.content.decode("utf-8")
        self.content = self.content.replace("```", "`\u200b`\u200b`\u200b")

    async def get_message(self) -> disnake.Message:
        f = io.StringIO(self.content)

        channel = random.choice(self.bot.send_guild.text_channels)
        message = await channel.send(file=disnake.File(fp=f, filename=self.filename))  # type: ignore
        return message

    @classmethod
    async def from_url(
        cls: Type[Self],
        *,
        bot: commands.Bot,
        url,
    ) -> Self:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                filename = url.split("?")[0].split("/")[-1]
        return cls(
            filename=filename,
            content=content,
            bot=bot,
        )

    async def to_url(self) -> str:
        return (await self.get_message()).attachments[0].url

    async def to_real(self) -> disnake.Attachment:
        return (await self.get_message()).attachments[0]


class EmbedFactory:
    @staticmethod
    def ide_embed(
        ctx: commands.Context, description: str, format_: str = "yaml"
    ) -> disnake.Embed:
        return (
            disnake.Embed(
                title="Jarvide Text Editor",
                description=f"```{format_}\n{description}```",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            .set_footer(
                text="The official jarvide text editor and ide. Expires in 5min"
            )
        )

    @staticmethod
    def code_embed(
        ctx: commands.Context,
        code: str,
        path: str,
        format_: str = "py",
        page_number: str = "",
    ) -> disnake.Embed:
        return (
            disnake.Embed(
                title="Jarvide Text Editor",
                description=f"**{path}**\n```{format_}\n{code}```{page_number}",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            .set_footer(text="The official jarvide text editor and ide")
        )


async def get_info(file_: File | disnake.Attachment) -> str:
    if isinstance(file_, disnake.Attachment):
        real_file = file_
    else:
        real_file = await file_.to_real()

    return (
        f"Opened file: {real_file.filename}"
        f"\nType: {real_file.content_type}"
        f"\nSize: {real_file.size // 1000} KB ({real_file.size:,} bytes)"
    )


class ExitButton(disnake.ui.Button):
    def __init__(self, ctx, bot_message, row=None):
        super().__init__(style=disnake.ButtonStyle.danger, label="Exit", row=row)
        self.bot_message = bot_message
        self.ctx = ctx

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            await interaction.response.defer()
        except disnake.errors.InteractionResponded:
            pass

        for child in self.view.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True

        embed = EmbedFactory.ide_embed(self.ctx, "Goodbye!")
        await self.bot_message.edit(view=self.view, embed=embed)


class SaveButton(disnake.ui.Button):
    def __init__(self, ctx, bot_message, file_: File, row=None):
        super().__init__(style=disnake.ButtonStyle.green, label="Save", row=row)
        self.bot_message = bot_message
        self.ctx = ctx
        self.file = file_

    async def callback(self, interaction: disnake.MessageInteraction):
        from src.cogs.ide.dialogs import SaveFile

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Save your file: {self.file.filename}\nCurrent directory: /",
        )
        await interaction.response.defer()
        await self.bot_message.edit(
            embed=embed, view=SaveFile(self.ctx, self.bot_message, self.file)
        )


def main_embed(bot):
    return (
        disnake.Embed(
            color=0x489CC4,
            title=f"{j}{a}{r}{v}{i}{d}{e}", 
            description=f"""
    **Hello, my name is Jarvide.**

    │ I am half AI, half discord [text editor](https://github.com/CaedenPH/Jarvide/wiki/Commands#jarvide-ide). │
    │ To get to know more about me read [this](https://github.com/CaedenPH/Jarvide/blob/main/ABOUT.md). │
    │ To understand more about how to use me, read the [wiki](https://github.com/CaedenPH/Jarvide/wiki). │
    │ Locate my FAQ's [here](https://github.com/CaedenPH/Jarvide/wiki#faq) │

    │ If you are still confused, join my [support server](https://discord.gg/mtue4UnWaA). │
    │ [My devs](https://discord.gg/mtue4UnWaA) are always around to assist you! │

    -----------------------------------------

    + My TOS can be located [here](https://github.com/CaedenPH/Jarvide/blob/main/TOS.md)
    + My privacy policy can be located [here](https://github.com/CaedenPH/Jarvide/blob/main/PrivacyPolicy.md)
            """,
        ).set_image(
            url="https://media.discordapp.net/attachments/926115595307614252/927951464725377034/big.png?width=1440"
                "&height=453 "
        ).set_author(
            name=f"Hello!",
            icon_url=bot.user.avatar.url
        ).set_footer(text="Jarvide's data is completely secure, so you shouldn't worry about data loss!")
    )
