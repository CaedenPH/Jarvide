import disnake

from disnake.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ide import File


class EditView(disnake.ui.View):
    def __init__(
            self,
            ctx,
            file_: "File",
            bot_message=None,
    ):
        self.ctx = ctx
        self.file = file_
        self.bot_message = bot_message
        super().__init__()

    @disnake.ui.button(label="Write", style=disnake.ButtonStyle.gray)
    async def write_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Replace", style=disnake.ButtonStyle.gray)
    async def replace_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Append", style=disnake.ButtonStyle.gray)
    async def append_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.blurple, row=2)
    async def next_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Prev", style=disnake.ButtonStyle.blurple, row=2)
    async def previous_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green, row=2)
    async def save_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.danger, row=3)
    async def exit_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Clear", style=disnake.ButtonStyle.danger, row=3)
    async def clear_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ): ...

    @disnake.ui.button(label="Project Settings", style=disnake.ButtonStyle.danger, row=3)
    async def settings_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from .ide import FileView
        await interaction.response.send_message(
            embed=disnake.Embed.from_dict(self.bot_message.embeds[0].to_dict()),
            view=FileView(self.ctx, self.file, self.bot_message)
        )


def setup(bot: commands.Bot):
    pass
