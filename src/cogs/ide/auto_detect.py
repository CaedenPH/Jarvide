import aiohttp
import base64
import disnake
import re

from disnake.ext import commands
from typing import Optional

from src.utils.utils import File, get_info, EmbedFactory
from src.cogs.ide.dialogs import FileView


class OpenIDEButton(disnake.ui.View):
    def __init__(self, ctx: commands.Context, file: File, bot_message):
        self.ctx = ctx
        self.file = file
        self.bot_message = bot_message
        super().__init__()

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Open in IDE", row=1)
    async def callback(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        description = await get_info(self.file)
        embed = EmbedFactory.ide_embed(self.ctx, description)
        view = FileView(self.ctx, self.file, self.bot_message)
        view.bot_message = await self.bot_message.edit(content=None, embed=embed, view=view)


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.ignore = True
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def github_url(self, message: disnake.Message) -> None:
        ctx = await self.bot.get_context(message)
        regex = re.compile(
            r"https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)/blob/(?P<branch>\w*)/(?P<path>[^#>]+)"
        )
        try:
            repo, branch, path = re.findall(regex, message.content)[0]
        except IndexError:
            return
        _message = await ctx.send("Fetching github link...")
        await message.edit(suppress=True)
        async with aiohttp.ClientSession() as session:
            a = await session.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            json = await a.json()
            if "content" not in json:
                b = await session.get(
                    f"https://raw.githubusercontent.com/{repo}/{branch}/{path}",
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                content = (await b.text()).replace("`", "`​")
                if content == "404: Not Found":
                    await ctx.send("Invalid github link.")
                    await _message.delete()
                    return
            else:
                content = base64.b64decode(json["content"]).decode("utf-8")
        file_ = File(content=content, filename=path.split("/")[-1], bot=self.bot)
        await _message.edit(content="Working github link found!", view=OpenIDEButton(ctx, file_, _message))

    @commands.Cog.listener("on_message")
    async def file_detect(self, message: disnake.Message) -> Optional[disnake.Message]:
        if not message.attachments:
            return
        ctx = await self.bot.get_context(message)
        real_file = message.attachments[0]
        _message = await ctx.send("Resolving file integrity...")
        try:
            file_ = File(
                content=await real_file.read(),
                filename=real_file.filename,
                bot=self.bot,
            )

        except UnicodeDecodeError:
            await message.delete()
            return await ctx.send("Unable to read file.", delete_after=10)
        await _message.edit(content="Readable file found!", view=OpenIDEButton(ctx, file_, _message))


def setup(bot):
    bot.add_cog(Listeners(bot))
