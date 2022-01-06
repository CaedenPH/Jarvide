import aiohttp
import base64
import disnake
import re
import random

from src.utils import EmbedFactory, File, get_info
from .file_view import FileView

THUMBS_UP = "👍"
bug_string = """
Thank you for reporting a bug! My team will work hard to solve this!


My team might want to ask you some questions, so we would love you to keep dm's open or join our support server! 
[ discord.gg/mtue4UnWaA ]
-----------------------------------------------------------
Bug id: {}"""

class OpenView(disnake.ui.View):
    def __init__(self, ctx, bot_message=None):
        super().__init__(timeout=300)
        self.bot_message = bot_message
        self.ctx = ctx
        self.bot = ctx.bot
        self.is_exited = False
        self.SUDO = self.ctx.me.guild_permissions.manage_messages

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True

        embed = EmbedFactory.ide_embed(
            self.ctx, "Ide timed out. Feel free to make a new one!"
        )
        await self.bot_message.edit(view=self, embed=embed)

    @disnake.ui.button(label="Upload", style=disnake.ButtonStyle.green)
    async def upload_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        num = 0
        await interaction.response.send_message("Upload a file!", ephemeral=True)

        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                if child.label != "Exit":
                    child.disabled = True
        await self.bot_message.edit(view=self)
        while not (
            message := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel
                and not self.is_exited
            )
        ).attachments:
            if self.SUDO:
                await message.delete()
            num += 1
            if num == 3:
                embed = EmbedFactory.ide_embed(
                    self.ctx, "Nice try. You can't break this bot!"
                )
                return await self.bot_message.edit(embed=embed)
            await interaction.channel.send("Upload a file", delete_after=5)

        real_file = message.attachments[0]
        try:
            file_ = File(
                content=await real_file.read(),
                filename=real_file.filename,
                bot=self.bot,
            )
        except UnicodeDecodeError:
            return await interaction.channel.send("Upload a valid text file!")
        await message.add_reaction(THUMBS_UP)

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
    async def github_button(
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
                    self.ctx, "Nice try. You can't break this bot!"
                )
                return await self.bot_message.edit(embed=embed)

            for child in self.children:
                if isinstance(child, disnake.ui.Button):
                    if child.label != "Exit":
                        child.disabled = True
            await self.bot_message.edit(view=self)
            url = await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel
                and not self.is_exited
            )
            await url.edit(suppress=True)
            regex = re.compile(
                r"https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)/blob/(?P<branch>\w*)/(?P<path>[^#>]+)"
            )
            try:
                repo, branch, path = re.findall(regex, url.content)[0]
                break
            except IndexError:
                await interaction.channel.send(
                    "Invalid github link, please try again.", delete_after=5
                )
                if self.SUDO:
                    await url.delete()

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
                    await interaction.channel.send(
                        "Invalid github link, please exit the IDE and try again.", delete_after=5
                    )
                    if self.SUDO:
                        await url.delete()
                    return
            else:
                content = json["content"]

                content = base64.b64decode(content).decode("utf-8")

        await url.add_reaction(THUMBS_UP)
        file_ = File(content=content, filename=url.content.split("/")[-1], bot=self.bot)
        description = await get_info(file_)
        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, file_, self.bot_message)
        )

    @disnake.ui.button(label="Link", style=disnake.ButtonStyle.green)
    async def link_button(
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

        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                if child.label != "Exit":
                    child.disabled = True
        await self.bot_message.edit(view=self)
        num = 0
        while not (
            message := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel
                and not self.is_exited
            )
        ).content.startswith(PASTE_URLS):
            if self.SUDO:
                await message.delete()
            else:
                await message.edit(suppress=True)

            num += 1
            if num == 3:
                embed = EmbedFactory.ide_embed(
                    self.ctx, "Nice try. You can't break this bot!"
                )
                return await self.bot_message.edit(embed=embed)
            await interaction.channel.send(
                f"That url is not supported! Our supported urls are {PASTE_URLS}",
                delete_after=5,
            )

        await interaction.channel.send("What would you like the filename to be?")
        filename = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel
            and not self.is_exited
        )

        await filename.add_reaction(THUMBS_UP)
        url = message.content.replace("/hastebin/", "/hastebin/raw/")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.read()

        file_ = File(filename=filename.content, content=text, bot=self.bot)
        description = await get_info(file_)
        embed = EmbedFactory.ide_embed(self.ctx, description)

        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, file_, self.bot_message)
        )

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def create_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                if child.label != "Exit":
                    child.disabled = True
        await self.bot_message.edit(view=self)
        await interaction.response.send_message(
            "What would you like the filename to be?", ephemeral=True
        )
        filename = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel
            and not self.is_exited
        )
        if len(filename.content) > 12:
            if self.SUDO:
                await filename.delete()
            return await interaction.channel.send(
                "That filename is too long! The maximum limit is 12 character"
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
        if content.startswith("```") and content.endswith("```"):
            clean_content = "\n".join(
                disnake.utils.remove_markdown(content).split("\n")[1:]
            )

        file_ = File(filename=filename, content=clean_content, bot=self.bot)
        description = await get_info(file_)

        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, file_, self.bot_message)
        )

    @disnake.ui.button(label="Saved", style=disnake.ButtonStyle.green)
    async def saved_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from . import OpenFromSaved

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Open a file from saved:\nCurrent directory: /",
        )
        await interaction.response.defer()
        await self.bot_message.edit(
            embed=embed, view=OpenFromSaved(self.ctx, self.bot_message)
        )

    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.danger)
    async def exit_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.is_exited = True
        await interaction.response.defer()

        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True

        embed = EmbedFactory.ide_embed(self.ctx, "Goodbye!")
        await self.bot_message.edit(view=self, embed=embed)

    @disnake.ui.button(label="Report a bug", style=disnake.ButtonStyle.blurple, row=1)
    async def report_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        responses = []

        for iteration, question in enumerate(['sum up your report in less than 10 words', 'explain your report. present as detailed of a description as you can provide, including button clicks, errors shown (if any), file open, and intention'], start=1):
            if iteration == 1:
                await interaction.response.send_message(f"Please {question}\nType q to end your report\nQuestion number {iteration}/2", ephemeral=True)
            else:
                await interaction.channel.send(f"Please {question}\nType q to end your report\nQuestion number {iteration}/2")

            message = await self.bot.wait_for("message", timeout=560, check=lambda m: 
                m.author == interaction.author
                and m.channel == interaction.channel
                and not self.is_exited,
            )
            if message.content.lower() == 'q':
                if self.SUDO:
                    await message.delete()
                return
            responses.append(message.content)

        embed = disnake.Embed(
            title=responses[0],
            description="```yaml\n" + responses[0] + "```",
            timestamp=interaction.message.created_at
        ).set_author(
            name=f"From {interaction.author.name}",
            icon_url=interaction.author.avatar.url
        )

        await self.bot.report_channel.send(embed=embed)
        bug_id = random.choice(self.bot.bugs)

        embed = EmbedFactory.ide_embed(self.ctx, bug_string.format(bug_id))
        await interaction.channel.send(embed=embed)