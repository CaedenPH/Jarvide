import disnake
import aiohttp
import io

from json.decoder import JSONDecodeError

from src.utils import (
    File,
    ExitButton,
    SaveButton,
    add_lines,
    EmbedFactory,
    LinePaginator,
    TextPaginator,
    get_info,
)
from .edit_view import EditView


class BackButton(disnake.ui.View):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()

    @disnake.ui.button(label="Back")
    async def back_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        real_file = await self.parent.file.to_real()
        description = (
            f"Opened file: {real_file.filename}"
            f"\nType: {real_file.content_type}"
            f"\nSize: {real_file.size // 1000} KB ({real_file.size:,} bytes)"
        )
        embed = EmbedFactory.ide_embed(self.parent.ctx, description)
        await self.parent.bot_message.edit(
            embed=embed,
            view=FileView(self.parent.ctx, self.parent.file, self.parent.bot_message),
        )


class FileView(disnake.ui.View):
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

    def __init__(self, ctx, file_: File, bot_message: disnake.Message = None):
        super().__init__(timeout=300)

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_
        self.SUDO = self.ctx.me.guild_permissions.manage_messages
        self.bot_message = bot_message
        self.extension = file_.extension

        self.add_item(ExitButton(ctx, bot_message, row=1))
        self.add_item(SaveButton(ctx, bot_message, file_, row=0))

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        content = add_lines(self.file.content)
        if len("".join(content)) < 2000:
            embed = EmbedFactory.ide_embed(
                self.ctx, "".join(content), format_=self.file.extension
            )
            return await self.bot_message.edit(embed=embed, view=BackButton(self))

        return await LinePaginator(
            interaction,
            content,
            prefix=f"```{self.file.extension}",
            suffix="```",
            line_limit=30,
            timeout=None,  # type: ignore
            embed_author_kwargs={
                "name": f"{self.ctx.author.name}'s automated paginator for {self.file.filename}",
                "icon_url": self.ctx.author.avatar.url,
            },
        ).start()

    @disnake.ui.button(label="Run", style=disnake.ButtonStyle.green)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = self.file.content
        name = self.extension

        async with aiohttp.ClientSession() as session:
            await interaction.response.defer()
            async with session.post(
                url="https://emkc.org/api/v1/piston/execute",
                json={"language": name, "source": content},
            ) as data:

                try:
                    json = await data.json()
                except (JSONDecodeError, aiohttp.ContentTypeError):
                    return await interaction.send(
                        "Something went wrong! Maybe the file is too long!",
                        delete_after=15,
                    )

                if "message" in json and "runtime is unknown" in json["message"]:
                    return await interaction.send(
                        "This file has an invalid file extension and therefore I do not know what language to run it in! Try renaming your file",
                        delete_after=15,
                    )

                if "output" not in json:
                    return await interaction.send(
                        "Something went wrong! Maybe the file is too long!",
                        delete_after=15,
                    )
                output = json["output"].strip("\n").strip()
                if not output:
                    output = "[No output]"

            await TextPaginator(
                interaction,
                f"```yaml\n{output}```",
                embed_author_kwargs={
                    "name": f"{self.ctx.author.name} evaluator for {self.file.filename}",
                    "icon_url": self.ctx.author.avatar.url,
                },
            ).start()

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.green)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        import math

        await interaction.response.defer()
        content: list[str] = add_lines(self.file.content)
        view = EditView(self)
        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx,
                "".join(content[:50]),
                self.file.filename,
                self.file.extension,
                f"\n1/{math.ceil(len(content) / 50)}",
            ),
            view=view,
        )

    @disnake.ui.button(label="Download", style=disnake.ButtonStyle.red, row=1)
    async def download_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        f = io.StringIO(self.file.content)
        await interaction.response.send_message(file=disnake.File(fp=f, filename=self.file.filename))  # type: ignore

    @disnake.ui.button(label="Rename", style=disnake.ButtonStyle.green)
    async def rename_button(
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
        if len(filename.content) > 12:
            if self.SUDO:
                await filename.delete()
            return await interaction.send(
                "That filename is too long! The maximum limit is 12 character"
            )

        file_ = File(filename=filename, content=self.file.content, bot=self.bot)
        description = await get_info(file_)

        self.file = file_
        self.extension = file_.filename.split(".")[-1]

        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(embed=embed)

    @disnake.ui.button(label="Move", style=disnake.ButtonStyle.red, row=1)
    async def move_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            f"What channel would you like to move this ide to? Send the channel #. Like {interaction.channel.mention}",
            ephemeral=True,
        )
        num = 0
        while not (
            channel := await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel,
            )
        ).channel_mentions:
            if self.SUDO:
                await channel.delete()
            num += 1
            if num == 3:
                embed = EmbedFactory.ide_embed(
                    self.ctx, "Nice try. You can't break this bot!"
                )
                return await self.bot_message.edit(embed=embed)
            await interaction.send("That is not a valid channel id!", delete_after=15)
        real_channel = channel.channel_mentions[0]

        if (
            real_channel in self.bot.active_commands
            and self.ctx.author in self.bot.active_commands[real_channel]
        ):
            return await interaction.send(
                "You already have an active IDE in that channel!"
            )

        embed = EmbedFactory.ide_embed(self.ctx, await get_info(self.file))

        self.ctx.channel = real_channel
        view = FileView(self.ctx, self.file)
        view.bot_message = await real_channel.send(embed=embed, view=view)

        if real_channel not in self.bot.active_commands:
            self.bot.active_commands[real_channel] = {}
        self.bot.active_commands[real_channel][self.ctx.author] = view.bot_message.id

        # disabling current
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True

        embed = EmbedFactory.ide_embed(self.ctx, "Goodbye!")
        await self.bot_message.edit(view=self, embed=embed)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.red, row=1)
    async def back_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from .open_view import OpenView

        await interaction.response.defer()
        await self.bot_message.edit(
            embed=EmbedFactory.ide_embed(self.ctx, "File open: No file currently open"),
            view=OpenView(self.ctx, self.bot_message),
        )
