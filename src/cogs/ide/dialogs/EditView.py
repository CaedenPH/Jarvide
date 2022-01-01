import disnake

from disnake.ext import commands
from typing import TYPE_CHECKING

from disnake.permissions import P

from src.utils.utils import *

if TYPE_CHECKING:
    from ..ide import File


class EditView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(
        self,
        ctx,
        file_: "File",
        bot_message=None,
    ):
        self.ctx = ctx
        self.file = file_
        self.content = file_.content
        self.bot_message = bot_message

        self.undo = []
        self.redo = []

        super().__init__()

    async def edit(self, inter):
        await inter.response.defer()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx, add_lines(self.content), self.file.filename
            ),
            view=EditView(self.ctx, self.file, self.bot_message),
        )

    @disnake.ui.button(label="Write", style=disnake.ButtonStyle.gray)
    async def write_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Replace", style=disnake.ButtonStyle.gray)
    async def replace_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Append", style=disnake.ButtonStyle.gray)
    async def append_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.blurple, row=2)
    async def next_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Prev", style=disnake.ButtonStyle.blurple, row=2)
    async def previous_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Undo", style=disnake.ButtonStyle.blurple, row=2)
    async def undo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  

        print(self.undo)
        if not self.undo:
            return await interaction.response.send_message("You have made no changes and have nothing to undo!", ephemeral=True)

    @disnake.ui.button(label="Redo", style=disnake.ButtonStyle.blurple, row=2)
    async def redo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green, row=2)
    async def save_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Clear", style=disnake.ButtonStyle.danger, row=3)
    async def clear_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        self.undo.append(self.content)
        self.content = ""  

        print(self.undo)

        await self.edit(interaction)    

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.danger, row=3)
    async def settings_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from .FileView import FileView

        embed = self.bot_message.embeds[0]
        embed.description = await get_info(self.file)

        await self.bot_message.edit(
            embed=embed,
            view=FileView(self.ctx, self.file, self.bot_message),
        )


    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.danger, row=3)
    async def exit_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message("Goodbye!")
        self.stop()

    

def setup(bot: commands.Bot):
    pass
