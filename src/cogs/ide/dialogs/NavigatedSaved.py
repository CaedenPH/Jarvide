import disnake
import time

from src.utils import *
from abc import ABC
from typing import Optional
from odmantic import Model

class FileModel(Model, ABC):
    user_id: int
    folder: Optional[str] = None
    name: str
    file_url: str
    create_epoch: int
    last_edit_epoch: Optional[float] = None

class DefaultButtons:
    def __init__(self):
        self.add_item(ExitButton(self.ctx, self.bot_message))

    @disnake.ui.button(label="CD", style=disnake.ButtonStyle.green)
    async def current_directory(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "What dir do you want to cd into?", ephemeral=True
        )
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )

    @disnake.ui.button(label="View folder", style=disnake.ButtonStyle.green)
    async def view_folder(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "What folder do you want to view?", ephemeral=True
        )
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )

        files = await self.bot.engine.find(FileModel, FileModel.user_id == self.ctx.author.id, FileModel.folder == directory)

        embed = EmbedFactory.ide_embed(
            self.ctx, 
            f"""All files:
            {files}""", 
        )

        await self.bot_message.edit(
            embed=embed,
        )


    @disnake.ui.button(label="Create folder", style=disnake.ButtonStyle.green)
    async def create_folder(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="All files", style=disnake.ButtonStyle.green)
    async def view_files(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):

        files = '\n    - '.join([f"{k.name}" for k in await self.bot.engine.find(FileModel, FileModel.user_id == self.ctx.author.id)])

        embed = EmbedFactory.ide_embed(
            self.ctx, 
            f"""All {self.ctx.author.name}'s files:
    - {files}""", 
        )   

        await interaction.response.defer()
        await self.bot_message.edit(
            embed=embed,
        )

    @disnake.ui.button(label="Delete folder", style=disnake.ButtonStyle.danger, row=2)
    async def delete_folder(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...
    
    @disnake.ui.button(label="Delete file", style=disnake.ButtonStyle.danger, row=2)
    async def delete_file(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "What file do you want to delete? Specify relative path", ephemeral=True
        )
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )


        filename = directory.content.split('/')[-1]
        file_ = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == filename,
        )  

        if not file_:
            await interaction.channel.send(f"File {file_} does not exist!")

        await self.bot.engine.delete(file_)
        await interaction.channel.send(f"Successfully deleted {file_.name}")



class OpenFromSaved(disnake.ui.View, DefaultButtons):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx, bot_message):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message
        self.SUDO = self.ctx.me.guild_permissions.manage_messages

    @disnake.ui.button(label="Select")
    async def select_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...


class SaveFile(disnake.ui.View, DefaultButtons):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx: commands.Context, bot_message: disnake.Message, file_: File):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message
        self.file = file_
        self.dir = f"/users/{ctx.author.name}"

        self.SUDO = self.ctx.me.guild_permissions.manage_messages
        
    @disnake.ui.button(label="Select", style=disnake.ButtonStyle.danger, row=2)
    async def select_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from . import FileView

        attachment = await self.file.to_real()

        all_files = [k.name for k in await self.bot.engine.find(FileModel, FileModel.user_id == self.ctx.author.id)]
        if self.file.filename in all_files:
            return await interaction.response.send_message(
                "You cant have a file with the same name!"
            )

        file_ = FileModel(
            file_url=attachment.url,
            name=self.file.filename,
            user_id = self.ctx.author.id,
            create_epoch = int(time.time()),
            folder=self.dir,
        )   
        
        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Saved {self.file.filename}\n--------------------\n{await get_info(attachment)}"
        )

        await interaction.response.defer()
        await self.bot.engine.save(file_)
        await self.bot_message.edit(
            embed=embed,
            view=FileView(self.ctx, self.file, self.bot_message)
        )
        