import disnake
import re
import base64

from disnake import message

from src.utils import *
from .FileView import FileView

THUMBS_UP = "👍"


class OpenView(disnake.ui.View):
    def __init__(self, ctx, bot_message: disnake.Message = None):
        super().__init__()
        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message

        self.clicked_num = 1

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.ctx.author == interaction.author:
            self.clicked_num += 1
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
            and self.clicked_num <= 2
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
                embed = EmbedFactory.ide_embed(
                    self.ctx, "Nice try. You cant break this bot!"
                )
                return await self.bot_message.edit(embed=embed)
            await interaction.channel.send("Upload a file", delete_after=15)
        await message.add_reaction(THUMBS_UP)

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
                embed = EmbedFactory.ide_embed(
                    self.ctx, "Nice try. You cant break this bot!"
                )
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
        await url.add_reaction(THUMBS_UP)

        content = base64.b64decode(content).decode("utf-8").replace("`", "`​")
        file_ = File(content=content, filename=url.content.split("/")[-1], bot=self.bot)

        description = await get_info(file_)
        embed = EmbedFactory.ide_embed(self.ctx, description)
        view = FileView(self.ctx, file_)
        view.bot_message = await self.bot_message.edit(embed=embed, view=view)

    @disnake.ui.button(label="Saved", style=disnake.ButtonStyle.green)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Link", style=disnake.ButtonStyle.green)
    async def fourth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        PASTE_URLS = (
            "https://www.toptal.com/developers/hastebin/",
            "https://pastebin.com/",
            "https://ghostbin.com/",
        )

        await interaction.response.send_message(
            "Send a url with code in it", ephemeral=True
        )
        while not (
            message := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel,
            )
        ).content.startswith(PASTE_URLS):
            await interaction.response.send_message(
                f"That url is not supported! Our supported urls are {PASTE_URLS}"
            )

        async with aiohttp.ClientSession() as session:
            async with session.get(message.content) as response:
                print(await response.read())

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def fifth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "What would you like the filename to be?", ephemeral=True
        )
        filename = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )

        await interaction.channel.send("What is the content?")
        message = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )
        await message.add_reaction(THUMBS_UP)
        content = message.content

        clean_content = content
        if content.startswith('```') and content.endswith('```'):
            clean_content = '\n'.join(disnake.utils.remove_markdown(content).split('\n')[1:])

        file_ = File(filename=filename, content=clean_content, bot=self.bot)
        description = await get_info(file_)

        embed = EmbedFactory.ide_embed(self.ctx, description)
        view = FileView(self.ctx, file_, self.bot_message)
        view.bot_message = await self.bot_message.edit(embed=embed, view=view)
