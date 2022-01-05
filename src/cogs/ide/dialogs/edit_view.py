from __future__ import annotations

import disnake

from disnake.ext import commands
from typing import TYPE_CHECKING, Literal

from src.utils.utils import EmbedFactory, ExitButton, SaveButton, add_lines, get_info

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


class OptionSelect(disnake.ui.Select):
    def __init__(
        self,
        ctx: commands.Context,
        file: File,
        pages: list[str],
        bot_message: disnake.Message,
        parent: EditView
    ):
        super().__init__()
        self.ctx = ctx
        self.bot_message = bot_message
        self.pages = pages
        self.file = file
        self.parent = parent
        self.options = [
            disnake.SelectOption(value="1", label="Find"),
            disnake.SelectOption(value="2", label="Go to page...")
        ]

    async def find_option(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            "What do you want to find? (Case-sensitive)", ephemeral=True
        )
        content: str = (
            await self.ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.author
                and m.channel == interaction.channel,
            )
        ).content
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
                break
            self.parent.page = line_occurrence[current_line] // 50
            await self.ctx.send(
                f"Found occurrence in line {line_occurrence[current_line] + 1}!",
                delete_after=10,
            )
            embed = self.bot_message.embeds[0]
            embed.description = f"```py\n{''.join(self.pages[line_occurrence[current_line] // 50])}\n```"
            await self.bot_message.edit(embed=embed, view=self.parent)
            await message.delete()

    async def goto_option(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Enter page number...", ephemeral=True)
        message: disnake.Message = (
            await self.ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.author
                and m.channel == interaction.channel,
            )
        )
        content = message.content
        await message.delete()
        if not content.isdigit():
            return await self.ctx.send("Not a digit, operation is cancelled.", delete_after=10)
        elif len(self.pages) < int(content) < 1:
            return await self.ctx.send("You cannot enter a number below 1 or above "
                                       "number of pages, operation is cancelled.",
                                       delete_after=10
                                       )
        self.parent.page = int(content) - 1
        embed = self.bot_message.embeds[0]
        embed.description = f"```py\n{''.join(self.pages[self.parent.page])}\n```"
        await self.bot_message.edit(embed=embed, view=self.parent)

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.message.delete()
        clicked = self.values[0]
        if clicked == "1":
            await self.find_option(interaction)
        elif clicked == "2":
            await self.goto_option(interaction)


class OptionView(disnake.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        file: File,
        pages: list[str],
        bot_message: disnake.Message,
        parent: EditView
    ):
        super().__init__()
        self.add_item(OptionSelect(ctx, file, pages, bot_message, parent))


class EditView(disnake.ui.View):
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

    def __init__(
        self,
        ctx,
        file_: "File",
        bot_message=None,
        file_view=None,
        lines: list[str] = None,
    ):
        super().__init__(timeout=120)

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_
        self.content = file_.content
        self.bot_message = bot_message
        self.file_view = file_view
        self.undo = self.file_view.file.undo
        self.redo = self.file_view.file.redo
        self.pages = [lines[x: x + 50] for x in range(0, len(lines), 50)]
        self.page = 0
        self.SUDO = self.ctx.me.guild_permissions.manage_messages

        self.add_item(ExitButton(ctx, bot_message, row=3))
        self.add_item(SaveButton(ctx, bot_message, file_, row=2))

    async def edit(self, inter):
        await inter.response.defer()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx,
                "".join(add_lines(self.file_view.file.content)),
                self.file.filename,
            ),
        )

    @disnake.ui.button(label="Options", style=disnake.ButtonStyle.gray)
    async def options_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "᲼",
            view=OptionView(self.ctx, self.file, self.pages, self.bot_message, self),
        )

    @disnake.ui.button(label="Replace", style=disnake.ButtonStyle.gray)
    async def replace_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "**Format:**\n[line number]\n```py\n<code>\n```**Example:**"
            "\n12-25\n```py\nfor i in range(10):\n\tprint('foo')\n```"
            "\n`[Click save to see the result]`",
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
            from_, to = 0, len(self.file_view.file.content) - 1
            code = clear_codeblock(content)
        self.undo.append(self.content)
        sliced = self.file_view.file.content.splitlines()
        del sliced[from_: to + 1]
        sliced.insert(from_, code)
        self.file_view.file.content = "\n".join(sliced)

    @disnake.ui.button(label="Append", style=disnake.ButtonStyle.gray)
    async def append_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "Type something... (This will append your code with a new line) `[Click save to see the result]`",
            ephemeral=True,
        )
        self.undo.append(self.file_view.file.content)
        self.file_view.file.content += "\n" + clear_codeblock(
            (
                await self.ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.author
                    and m.channel == interaction.channel,
                )
            ).content
        )

    @disnake.ui.button(label="Rename", style=disnake.ButtonStyle.grey)
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
            return await interaction.channel.send(
                "That filename is too long! The maximum limit is 12 character"
            )

        file_ = File(filename=filename, content=self.file.content, bot=self.bot)
        description = await get_info(file_)

        self.file = file_
        self.extension = file_.filename.split(".")[-1]

        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(embed=embed)

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
                description=f"```py\n{''.join(self.pages[self.page])}\n```\nPage: {self.page + 1}/{len(self.pages)}",
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
                description=f"```py\n{''.join(self.pages[self.page])}\n```\nPage: {self.page + 1}/{len(self.pages)}",
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

        self.redo.append(self.file_view.file.content)
        self.file_view.file.content = self.undo.pop(-1)
        await self.edit(interaction)

    @disnake.ui.button(label="Redo", style=disnake.ButtonStyle.blurple, row=2)
    async def redo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if not self.redo:
            return await interaction.response.send_message(
                "You have made no changes and have nothing to undo!", ephemeral=True
            )

        self.undo.append(self.file_view.file.content)
        self.file_view.file.content = self.redo.pop(-1)
        await self.edit(interaction)

    @disnake.ui.button(label="Clear", style=disnake.ButtonStyle.danger, row=3)
    async def clear_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.undo.append(self.file_view.file.content)
        self.file_view.file.content = ""

        await self.edit(interaction)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.danger, row=3)
    async def settings_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        embed = EmbedFactory.ide_embed(self.ctx, await get_info(self.file))
        self.undo = []
        self.redo = []
        await self.bot_message.edit(embed=embed, view=self.file_view)


def setup(bot: commands.Bot):
    pass
