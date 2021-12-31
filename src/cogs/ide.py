import aiohttp
import base64
from attr import has
import disnake
import re
import os

from disnake import message
from disnake.ext.commands import bot

from ..utils import TextPaginator
from disnake.ext import commands
from typing import TypeVar

Self = TypeVar("Self")


class IncorrectInstance(Exception):
    """User passed incorrect instance"""

    def __init__(self, argument: str) -> None:
        print(self, dir(self))
        super().__init__(f"{argument}")


class File():
    TEMP = "./temp/"

    def __init__(
        self,
        *,
        filename,
        content,
        bot,
    ) -> None:
        self.filename = filename
        self.bot = bot
        self.content = content

        self.setup()
    
    def setup(self) -> None:
        if hasattr(self.filename, 'content'):
            self.filename = self.filename.content
        if hasattr(self.content, 'content'):
            self.content = self.content.content
        if hasattr(self.content, 'decode'):
            self.content = self.content.decode("utf-8")
        self.content = self.content.replace(
            "```", "`\u200b`\u200b`\u200b"
        )

    async def get_message(self) -> disnake.Message:
        FP = self.TEMP + self.filename
        if self.filename in os.listdir(self.TEMP):
            os.remove(FP)
        with open(FP, "w") as _file:
            _file.write(self.content)

        message = await self.bot.channel.send(file=disnake.File(FP))
        return message

    @classmethod
    async def from_url(
        cls: Self,
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
    def code_embed(ctx: commands.Context, code: str, path: str, format_: str = "py"):
        return (
            disnake.Embed(
                title="Jarvide Text Editor",
                description=f"**{path}**\n```{format_}\n{code}```",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            .set_footer(text="The official jarvide text editor and ide")
        )


class FileView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(
        self, 
        ctx, 
        file_: File, 
        bot_message: disnake.Message,
    ):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_
        self.bot_message = bot_message

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = self.file.content
        if len(content) < 2000:
            embed = EmbedFactory.ide_embed(self.ctx, content, format_=self.file.filename.split('.')[-1])
            return await interaction.response.send_message(embed=embed)

    @disnake.ui.button(label="Run", style=disnake.ButtonStyle.green)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):

        content = self.file.content
        name = self.file.filename.split(".")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://emkc.org/api/v1/piston/execute",
                json={"language": name[-1], "source": content},
            ) as data:

                paginator = await TextPaginator(interaction, f"```yaml\n{(await data.json())['output']}```").start()
                

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.green)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...


class OpenView(disnake.ui.View):
    def __init__(
        self, 
        ctx, 
    ):
        super().__init__()
        self.ctx = ctx
        self.bot = ctx.bot

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @disnake.ui.button(label="Upload", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        

        num = 0
        await interaction.response.send_message("Upload a file!", ephemeral=True)
        while not (
            message := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel,
            )
        ).attachments:
            num += 1
            if num == 3:
                embed = EmbedFactory.ide_embed(self.ctx, "Nice try. You cant break this bot!")
                return await self.bot_message.edit(embed = embed)
            await interaction.channel.send("Upload a file", delete_after=15)
            

        real_file = message.attachments[0]
        file_ = File(
            content=await real_file.read(), 
            filename=real_file.filename,
            bot=self.bot,
        )

        description = (
            f"Opened file: {real_file.filename}"
            f"\nType: {real_file.content_type}"
            f"\nSize: {real_file.size // 1000} KB ({real_file.size:,} bytes)"
        )
        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(
            content=None, embed=embed, view=FileView(self.ctx, file_, self.bot_message)
        )

    @disnake.ui.button(label="Github", style=disnake.ButtonStyle.green)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "Send a github repository link!", ephemeral=True
        )
        num = 0
        while True:
            num += 1
            if num == 3:
                embed = EmbedFactory.ide_embed(self.ctx, "Nice try. You cant break this bot!")
                return await self.bot_message.edit(embed=embed)
                
            url = await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel,
            )
            await url.edit(suppress=True)
            regex = re.compile(
                r"https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)"
                r"/blob/(?P<branch>\w*)/(?P<path>[^#>]+)"
            )
            try:
                repo, branch, path = re.findall(regex, url.content)[0]
                break
            except IndexError:
                await interaction.channel.send(
                    "Not a valid github link, please try again."
                )
        async with aiohttp.ClientSession() as session:
            a = await session.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            content = (await a.json())["content"]
        decoded_string = base64.b64decode(content).decode("utf-8").replace("`", "`​")
        enumerated = list(enumerate(decoded_string.split("\n")))
        lines = []
        for number, line in enumerated:
            number = ("0" * (len(str(enumerated[-1][0])) - len(str(number)))) + str(
                number
            )
            line = f"\n{number} | {line}"
            lines.append(line)

        lines = "".join(lines)

        file_ = File(
            content=lines, 
            filename=url.split('/')[-1],
            bot=self.bot
        )
        
        real_file = await file_.to_real()

        description = (
            f"Opened file: {real_file.filename}"
            f"\nType: {real_file.file_.content_type}"
            f"\nSize: {real_file.file_.size // 1000} KB ({file_.size:,} bytes)"
        )
        embed = EmbedFactory.ide_embed(self.ctx, description)

        await self.bot_message.edit(embed=embed, view=FileView(self.ctx, file_, self.bot_message))

    @disnake.ui.button(label="Saved", style=disnake.ButtonStyle.green)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Link", style=disnake.ButtonStyle.green)
    async def fourth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        PASTE_URLS = ("https://www.toptal.com/developers/hastebin/", "https://pastebin.com/",
                                 "https://ghostbin.com/")

        await interaction.response.send_message("Send a url with code in it", ephemeral=True)
        while not (
            message := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel,
            )).content.startswith(PASTE_URLS):
            await interaction.response.send_message(f"That url is not supported! Our supported urls are {PASTE_URLS}")

        async with aiohttp.ClientSession() as session:
            async with session.get(message.content) as response:
                print(await response.read())

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def fifth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        

        await interaction.response.send_message("What would you like the filename to be?", ephemeral=True)
        filename = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel,
        )   

        await interaction.channel.send("What is the content?")
        content = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel,
        )

        file_ = File(
            filename=filename,
            content=content,
            bot=self.bot
        )
        real_file = await file_.to_real()
        description = (
            f"Opened file: {real_file.filename}"
            f"\nType: {real_file.content_type}"
            f"\nSize: {real_file.size // 1000} KB ({real_file.size:,} bytes)"
        )


        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(embed=embed, view=FileView(self.ctx, file_, self.bot_message))



class Ide(commands.Cog):
    """Ide cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ide(self, ctx: commands.Context) -> None:
        embed = EmbedFactory.ide_embed(ctx, "File open: No file currently open")
        view = OpenView(ctx)
        view.bot_message = await ctx.send(embed=embed, view=view)


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""
    bot.add_cog(Ide(bot))
