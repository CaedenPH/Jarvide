from __future__ import annotations

import datetime
import disnake
import time

from argparse import ArgumentParser
from typing import TYPE_CHECKING, Literal

from src.utils.utils import EmbedFactory, ExitButton, SaveButton, add_lines, get_info
from src.utils import LinePaginator

if TYPE_CHECKING:
    from src.utils import File


def clear_codeblock(content: str):
    content.strip("\n")
    if content.startswith("```"):
        content = "\n".join(content.splitlines()[1:])
    if content.endswith("```"):
        content = content[:-3]
    if "`" in content:
        content.replace("`", "\u200b")
    return content


def page_integrity(page: int, pages: int, method: Literal["back", "next"]):
    if page == 0:
        if method == "back":
            return False
        return True
    elif page == (pages - 1):
        if method == "back":
            return True
        return False
    return True


class RestoreVersion(disnake.ui.Button):
    def __init__(self, parent, row: int = 1):
        super().__init__(
            style=disnake.ButtonStyle.green, label="Restore Version", row=row
        )
        self.parent = parent
        self.bot_message = self.parent.parent.bot_message
        self.ctx = self.parent.parent.ctx

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            "Successfully restored version!", ephemeral=True
        )
        self.parent.parent.file.content = self.parent.parent.file.version_history[
            int(self.parent.values[0])
        ]
        await self.parent.parent.parent.refresh_message(0)


class VersionHistorySelect(disnake.ui.Select):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.options = []
        self.functions = {}

        for k in self.parent.parent.version_history.keys():
            self.options.append(
                disnake.SelectOption(
                    value=str(k), label=str(datetime.datetime.fromtimestamp(k))
                )
            )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        lines = add_lines(
            self.parent.parent.version_history[int(interaction.values[0])]
        )
        if len(lines) <= 50:
            view = disnake.ui.View()
            view.add_item(RestoreVersion(self))
            # view.add_item(ExitButton(self.parent.ctx, self.parent.bot_message, row=1)) || Make this deletes version history message, not bot_message
            embed = EmbedFactory.ide_embed(
                self.parent.ctx, "".join(lines), format_=self.parent.file.extension
            )
            return await self.parent.ctx.send(embed=embed, view=view)

        paginator = LinePaginator(
            interaction,
            lines,
            prefix=f"```{self.parent.file.extension}",
            suffix="```",
            line_limit=30,
            timeout=None,  # type: ignore
            embed_author_kwargs={
                "name": f"{self.parent.ctx.author.name}'s automated paginator for {self.parent.file.filename}",
                "icon_url": self.parent.ctx.author.avatar.url,
            },
        )
        paginator.add_item(RestoreVersion(self))
        await paginator.start()


class VersionHistoryView(disnake.ui.View):
    def __init__(self, parent):
        super().__init__()
        self.add_item(VersionHistorySelect(parent))


class OptionSelect(disnake.ui.Select):
    def __init__(self, parent: EditView):
        super().__init__()
        self.parent = parent
        self.ctx = self.parent.ctx
        self.bot_message = self.parent.bot_message
        self.file = self.parent.file
        self.pages = self.parent.pages
        self.options = [
            disnake.SelectOption(value="1", label="Find"),
            disnake.SelectOption(value="2", label="Go to page..."),
            disnake.SelectOption(value="3", label="Version History"),
        ]

    @staticmethod
    def suppress_argparse(statement, *args, **kwargs):
        try:
            return statement(*args, **kwargs)
        except BaseException:
            pass

    async def find_option(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            "What do you want to find? (Case-sensitive)\n"
            "For advanced use look the available flags below:\n"
            "\t`-replace <*chars>`: Replace every occurrence with `chars`\n"
            "\n**Example:**\n```\n-replace foo\nbar\n```",
            ephemeral=True,
        )
        content: str = (
            await self.ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.author
                and m.channel == interaction.channel,
            )
        ).content
        parser = ArgumentParser(add_help=False, allow_abbrev=False)
        parser.add_argument("-replace", nargs="+")
        args = self.suppress_argparse(
            parser.parse_args, content.splitlines()[0].split()
        )
        if content.startswith("-"):
            content = "".join(content.splitlines()[1:])
        if args.replace:
            self.parent.create_undo()
            self.file.content = self.file.content.replace(
                content, "".join(args.replace)
            )
            await self.parent.refresh_message(self.parent.page)
            return await self.ctx.send(
                f"Replaced all `{content}` occurrences with `{''.join(args.replace)}`!"
            )

        try:
            page_occurrence = [
                i for i, c in enumerate(self.pages) if any([content in li for li in c])
            ]
        except IndexError:
            return await self.ctx.send("No occurrence found!")
        lines = self.file.content.splitlines()
        line_occurrence = [i for i, c in enumerate(lines) if content in c]
        current_line = 0
        await self.ctx.send(
            f"Found {self.file.content.count(content)} occurrence of `{content}` "
            f"({len(line_occurrence)} lines, {len(page_occurrence)} pages) "
            f'in **{self.file.filename}**! [Type "next" or "back" to go '
            f'to the next or last occurrence, or "quit" to quit the search!]'
        )
        while True:
            message: disnake.Message = await self.ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.author
                and m.channel == interaction.channel
                and m.content.lower() in ("back", "next", "quit"),
                timeout=60,
            )
            if message.content.lower() == "back":
                if page_integrity(current_line, len(line_occurrence), "back"):
                    current_line -= 1
                else:
                    current_line = len(line_occurrence) - 1
            elif message.content.lower() == "next":
                if page_integrity(current_line, len(line_occurrence), "next"):
                    current_line += 1
                else:
                    current_line = 0
            else:
                await self.ctx.send("Exited!", delete_after=10)
                break
            self.parent.page = line_occurrence[current_line] // 50
            await self.ctx.send(
                f"Found occurrence in line {line_occurrence[current_line] + 1}!",
                delete_after=10,
            )
            await self.parent.refresh_message(line_occurrence[current_line] // 50)
            await message.delete()

    async def goto_option(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Enter page number...", ephemeral=True)
        message: disnake.Message = await self.ctx.bot.wait_for(
            "message",
            check=lambda m: m.author == interaction.author
            and m.channel == interaction.channel,
        )
        content = message.content
        await message.delete()
        if not content.isdigit():
            return await self.ctx.send(
                "Not a digit, operation is cancelled.", delete_after=10
            )
        elif len(self.pages) < int(content) < 1:
            return await self.ctx.send(
                "You cannot enter a number below 1 or above "
                "number of pages, operation is cancelled.",
                delete_after=10,
            )
        self.parent.page = int(content) - 1
        await self.parent.refresh_message(self.parent.page)

    async def version_history(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            "Showing version history...", view=VersionHistoryView(self)
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        clicked = self.values[0]
        if clicked == "1":
            await self.find_option(interaction)
        elif clicked == "2":
            await self.goto_option(interaction)
        elif clicked == "3":
            await self.version_history(interaction)


class OptionView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.parent.ctx.author
            and interaction.channel == self.parent.ctx.channel
        )

    def __init__(self, parent: EditView):
        self.parent = parent

        super().__init__()
        self.add_item(OptionSelect(parent))


class EditView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:

        self.writing_mode = False

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

    def __init__(self, file_view=None):
        super().__init__(timeout=120)
        self.parent = file_view

        self.ctx = self.parent.ctx
        self.bot = self.parent.ctx.bot
        self.file = self.parent.file
        self.bot_message = self.parent.bot_message
        self.undo = self.parent.file.undo
        self.redo = self.parent.file.redo
        self.version_history = self.parent.file.version_history
        self.page = 0
        self.writing_mode = False
        self.extension = None
        self.SUDO = self.ctx.me.guild_permissions.manage_messages

        self.add_item(
            SaveButton(
                self.parent.ctx, self.parent.bot_message, self.parent.file, row=3
            )
        )
        self.add_item(ExitButton(self.parent.ctx, self.parent.bot_message, row=3))

    def create_undo(self):
        self.undo.append(self.file.content)
        self.version_history[int(time.time())] = self.file.content

    @property
    def pages(self):
        lines = add_lines(self.file.content)
        return ["".join(lines[x: x + 50]) for x in range(0, len(lines), 50)]

    async def refresh_message(self, page):
        embed = self.bot_message.embeds[0]
        pages = self.pages
        embed.description = f"```{self.file.extension}\n{''.join(pages[page])}\n```\n{page + 1}/{len(pages)}"
        await self.bot_message.edit(embed=embed, view=self)

    async def edit(self, inter):
        await inter.response.defer()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx,
                "".join(add_lines(self.file.content)),
                self.file.filename,
            ),
        )

    @disnake.ui.button(label="Options", style=disnake.ButtonStyle.gray)
    async def options_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "᲼",
            view=OptionView(self),
        )

    @disnake.ui.button(label="Replace", style=disnake.ButtonStyle.gray)
    async def replace_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "**Format:**\n[line number]\n```py\n<code>\n```**Example:**"
            "\n12-25\n```py\nfor i in range(10):\n\tprint('foo')\n```",
            ephemeral=True,
        )
        content: str = (
            await self.ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.author
                and m.channel == interaction.channel,
            )
        ).content
        if content[0].isdigit():
            line_no = content.splitlines()[0]
            if "-" in line_no:
                from_, to = (
                    int(line_no.split("-")[0]) - 1,
                    int(line_no.split("-")[1]) - 1,
                )
            else:
                from_, to = int(line_no) - 1, int(line_no) - 1
            code = clear_codeblock("\n".join(content.splitlines()[1:]))
        else:
            from_, to = 0, len(self.file.content) - 1
            code = clear_codeblock(content)
        sliced = self.file.content.splitlines()
        del sliced[from_: to + 1]
        sliced.insert(from_, code)
        self.create_undo()
        self.file.content = "\n".join(sliced)
        await self.refresh_message(self.page)

    @disnake.ui.button(label="Append", style=disnake.ButtonStyle.gray)
    async def append_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "Type something... (This will append your code with a new line) `[Click save to see the result]`",
            ephemeral=True,
        )
        self.file.content += "\n" + clear_codeblock(
            (
                await self.ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.author
                    and m.channel == interaction.channel,
                )
            ).content
        )
        await self.refresh_message(self.page)

    @disnake.ui.button(label="Writer mode", style=disnake.ButtonStyle.grey)
    async def writer_mode(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "Hello! Welcome to writer mode. In this mode every message you send will write to your open file\n"
            "If you want to the bot to ignore your message, start it with !\n"
            "To end this mode either click another button or type q\n"
            "This will time out after 5 minutes without a response\n",
            ephemeral=True,
        )

        self.writing_mode = True
        while message := await self.ctx.bot.wait_for(
            "message",
            check=lambda m: m.author == interaction.author
            and m.channel == interaction.channel,
        ):
            content = message.content.lower()
            if not self.writing_mode:
                return
            if content == "q":
                return await interaction.send("You have exited writer mode!")
            if content.startswith("!"):
                continue

            self.file.content += "\n" + clear_codeblock(content)
            self.create_undo()
            await self.refresh_message(self.page)

    @disnake.ui.button(label="Prev", style=disnake.ButtonStyle.blurple, row=2)
    async def previous_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        if page_integrity(self.page, len(self.pages), "back"):
            self.page -= 1
        else:
            self.page = len(self.pages) - 1
        embed = (
            disnake.Embed(
                description=f"```{self.file.extension}\n"
                f"{''.join(self.pages[self.page])}\n```\nPage: {self.page + 1}/{len(self.pages)}",
                timestamp=self.ctx.message.created_at,
            )
            .set_author(
                name=f"{self.ctx.author.name}'s automated paginator for {self.file.filename}",
                icon_url=self.ctx.author.avatar.url,
            )
            .set_footer(text="The official jarvide text editor and ide")
        )
        await self.bot_message.edit(embed=embed, view=self)

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.blurple, row=2)
    async def next_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        if page_integrity(self.page, len(self.pages), "next"):
            self.page += 1
        else:
            self.page = 0
        embed = (
            disnake.Embed(
                description=f"```{self.file.extension}\n{''.join(self.pages[self.page])}"
                f"\n```\nPage: {self.page + 1}/{len(self.pages)}",
                timestamp=self.ctx.message.created_at,
            )
            .set_author(
                name=f"{self.ctx.author.name}'s automated paginator for {self.file.filename}",
                icon_url=self.ctx.author.avatar.url,
            )
            .set_footer(text="The official jarvide text editor and ide")
        )
        await self.bot_message.edit(embed=embed, view=self)

    @disnake.ui.button(label="Undo", style=disnake.ButtonStyle.blurple, row=2)
    async def undo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if not self.undo:
            return await interaction.response.send_message(
                "You have made no changes and have nothing to undo!", ephemeral=True
            )

        self.redo.append(self.file.content)
        self.create_undo()
        self.file.content = self.undo.pop(-1)
        await self.edit(interaction)

    @disnake.ui.button(label="Redo", style=disnake.ButtonStyle.blurple, row=2)
    async def redo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if not self.redo:
            return await interaction.response.send_message(
                "You have made no changes and have nothing to undo!", ephemeral=True
            )
        self.create_undo()
        self.file.content = self.redo.pop(-1)
        await self.edit(interaction)

    @disnake.ui.button(label="Rename", style=disnake.ButtonStyle.green, row=3)
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

    @disnake.ui.button(label="Clear", style=disnake.ButtonStyle.danger, row=3)
    async def clear_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.create_undo()
        self.file.content = ""

        await self.edit(interaction)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.danger, row=3)
    async def settings_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        embed = EmbedFactory.ide_embed(self.ctx, await get_info(self.file))
        self.undo = []
        self.redo = []
        await self.bot_message.edit(embed=embed, view=self.parent)


def setup(bot: Jarvide):
    pass
