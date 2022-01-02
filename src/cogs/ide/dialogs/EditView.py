import disnake

from disnake.ext import commands
from typing import TYPE_CHECKING

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
        super().__init__()

        self.ctx = ctx
        self.file = file_
        self.content = file_.content
        self.bot_message = bot_message

        self.undo = []
        self.redo = []  

        self.add_item(ExitButton(row=3))


    async def edit(self, inter):
        await inter.response.defer()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx, "".join(add_lines(self.content)), self.file.filename
            ),
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

        if not self.undo:
            return await interaction.response.send_message("You have made no changes and have nothing to undo!", ephemeral=True)

        self.redo.append(self.content)
        self.content = self.undo[-1]    
        await self.edit(interaction)

    @disnake.ui.button(label="Redo", style=disnake.ButtonStyle.blurple, row=2)
    async def redo_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if not self.redo:
            return await interaction.response.send_message("You have made no changes and have nothing to undo!", ephemeral=True)

        self.undo.append(self.content)
        self.content = self.redo[-1]    
        await self.edit(interaction)

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green, row=3)
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
    

def setup(bot: commands.Bot):
    pass
