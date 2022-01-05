import disnake
import time

from disnake.ext import commands
from typing import Optional
from odmantic import Model

from src.utils import ExitButton, EmbedFactory, File, get_info


class FileModel(Model):  # noqa
    user_id: int
    name: str
    file_url: Optional[str] = None
    folder: Optional[str] = None
    create_epoch: float
    last_edit_epoch: Optional[float] = None


class DefaultButtons(disnake.ui.View):
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

    def __init__(self, ctx, bot_message):
        self.ctx = ctx
        self.bot_message = bot_message
        self.bot = ctx.bot
        self.path = "/"

        self.SUDO = self.ctx.me.guild_permissions.manage_messages
        super().__init__(timeout=300)

    @disnake.ui.button(label="Move dir", style=disnake.ButtonStyle.green)
    async def current_directory(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message("What folder would you like to move into?", ephemeral=True)
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )
        path = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.folder == self.path,
            FileModel.name == "folder: " + directory.content
        )

        if not path:
            if self.SUDO:
                await directory.delete()
            return await interaction.channel.send(
                f"{directory.content} doesn't exist!", delete_after=15
            )
        self.path = f"{self.path}{path.name[8:]}/"
        embed = EmbedFactory.ide_embed(
            self.ctx, f"Moved into dir: {self.path}\n"
                      f"{''.join(['-' for _ in range(len(self.path) + len('Moved into dir: '))])}"
        )

        await self.bot_message.edit(
            embed=embed
        )

    @disnake.ui.button(label="View folder", style=disnake.ButtonStyle.green)
    async def view_folder(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        files = "\n    - ".join(
            [
                f"{k.name}"
                for k in await self.bot.engine.find(
                    FileModel,
                    FileModel.user_id == self.ctx.author.id,
                    FileModel.folder == self.path,
                )
            ]
        )

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"""{self.path}:
    - {files}""",
        )

        await interaction.response.defer()
        await self.bot_message.edit(
            embed=embed,
        )

    @disnake.ui.button(label="New folder", style=disnake.ButtonStyle.green)
    async def create_folder(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        await interaction.response.send_message("What is the name of the folder you would like to create?", ephemeral=True)
        folder = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )
        if len(folder.content) >= 12:
            if self.SUDO:
                await folder.delete()
            return await interaction.channel.send("The folder name has to be less than 12 characters long!", delete_after=15)

        dir_files = [
            k.name
            for k in await self.bot.engine.find(
                FileModel,
                FileModel.user_id == self.ctx.author.id,
                FileModel.folder == self.path,
                FileModel.name == folder.content
            )
        ]
        if folder.content in dir_files:
            return await interaction.response.send_message(
                "You can't have a folder in with the same name!"
            )

        folder_ = FileModel(
            name="folder: " + folder.content,
            user_id=self.ctx.author.id,
            create_epoch=int(time.time()),
            folder=self.path,
        )

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Created {folder.content}\n{''.join(['-' for _ in range(len(folder.content)+len('Created '))])}\nCurrent directory: {self.path}",
        )

        await self.bot.engine.save(folder_)
        await self.bot_message.edit(embed=embed)

    @disnake.ui.button(label="All files", style=disnake.ButtonStyle.green)
    async def view_files(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        files = "\n    - ".join(
            [
                f"{k.name}"
                for k in await self.bot.engine.find(
                    FileModel, 
                    FileModel.user_id == self.ctx.author.id
                )
            ]
        )

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"""/:
    - {files}""",
        )

        await interaction.response.defer()
        await self.bot_message.edit(
            embed=embed,
        )

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.danger, row=2)
    async def delete_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "What file/folder do you want to delete? Specify relative path", ephemeral=True
        )
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )

        filename = directory.content.split("/")[-1]
        file_ = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == filename,
            FileModel.folder == self.path,
        )

        if file_:
            await self.bot.engine.delete(file_)
            return await interaction.channel.send(f"Successfully deleted {file_.name}")

        folder = directory.content
        if directory.content.endswith("/"):
            folder = directory.content.split("/")[-2]

        folder_ = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == "folder: " + folder,
            FileModel.folder == self.path,
        )
         
        if folder_:
            await self.bot.engine.delete(folder_)
            await interaction.channel.send(f"Successfully deleted {file_.name}") 
        
        await interaction.channel.send(f"I could not find a folder or file called {directory.content} in {self.path}") 


class OpenFromSaved(DefaultButtons):
    def __init__(self, ctx, bot_message):
        super().__init__(ctx, bot_message)

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message
        self.add_item(ExitButton(self.ctx, self.bot_message, row=2))

    @disnake.ui.button(label="Select file", style=disnake.ButtonStyle.danger, row=2)
    async def select_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        from . import FileView

        await interaction.response.send_message(
            "What file do you want to open?", ephemeral=True
        )
        filename = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )

        file_model = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == filename.content,
            FileModel.folder == self.path,
        )

        if not file_model:
            if self.SUDO:
                await filename.delete()
            return await interaction.channel.send(f"{filename.content} doesnt exist!", delete_after=15)

        file_ = await File.from_url(bot=self.bot, url=file_model.file_url)
        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Opened {filename.content}\n{''.join(['-' for _ in range(len(filename.content)+len('Opened '))])}\n{await get_info(file_)}",
        )

        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, file_, self.bot_message)
        )


class SaveFile(DefaultButtons):
    def __init__(
        self, ctx: commands.Context, bot_message: disnake.Message, file_: File
    ):
        super().__init__(ctx, bot_message)

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message
        self.file = file_
        self.add_item(ExitButton(self.ctx, self.bot_message, row=2))

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.danger, row=2)
    async def save_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from . import FileView

        attachment = await self.file.to_real()

        dir_files = [
            k.name
            for k in await self.bot.engine.find(
                FileModel,
                FileModel.user_id == self.ctx.author.id,
                FileModel.folder == self.path,
            )
        ]
        file_ = FileModel(
            file_url=attachment.url,
            name=self.file.filename,
            user_id=self.ctx.author.id,
            create_epoch=int(time.time()),
            folder=self.path,
        )
        overwrote = f"Overwrote file {self.file.filename}" + ''.join(['-' for _ in range(len(self.file.filename)+len('Saved '))]) + "\n"
        n = '\n'
        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Saved {self.file.filename}\n{''.join(['-' for _ in range(len(self.file.filename)+len('Saved '))])}{overwrote if self.file.filename in dir_files else n}{await get_info(attachment)}",
        )

        await interaction.response.defer()
        await self.bot.engine.save(file_)
        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, self.file, self.bot_message)
        )
