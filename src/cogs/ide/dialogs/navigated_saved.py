import disnake
import time

from disnake.ext import commands
from typing import Optional
from odmantic import Model

from src.utils import ExitButton, EmbedFactory, File, get_info


class FileModel(Model):  # noqa
    user_id: int
    file_url: Optional[str]
    name: str
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
        self.add_item(ExitButton(self.ctx, self.bot_message))

    @disnake.ui.button(label="Move dir", style=disnake.ButtonStyle.green)
    async def current_directory(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message("What folder ", ephemeral=True)
        directory = await self.bot.wait_for(
            "message",
            check=lambda m: self.ctx.author == m.author
            and m.channel == self.ctx.channel,
        )
        path = self.bot.engine.find(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.folder == directory,
        )

        if not path:
            if self.SUDO:
                await directory.delete()
            return await interaction.channel.send(
                f"{directory} doesn't exist!", delete_after=15
            )

        embed = EmbedFactory.ide_embed(self.ctx, f"")

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
            f"""All {self.ctx.author.name}'s files in current directory ({self.path}):
    - {files}""",
        )

        await interaction.response.defer()
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

        files = "\n    - ".join(
            [
                f"{k.name}"
                for k in await self.bot.engine.find(
                    FileModel, FileModel.user_id == self.ctx.author.id
                )
            ]
        )

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

        filename = directory.content.split("/")[-1]
        file_ = await self.bot.engine.find_one(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == filename,
        )

        if not file_:
            if self.SUDO:
                await directory.delete()
            return await interaction.channel.send(f"File {file_} does not exist!")

        await self.bot.engine.delete(file_)
        await interaction.channel.send(f"Successfully deleted {file_.name}")


class OpenFromSaved(DefaultButtons):
    def __init__(self, ctx, bot_message):
        super().__init__(ctx, bot_message)

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = bot_message

    @disnake.ui.button(label="Select file", style=disnake.ButtonStyle.danger, row=2)
    async def select_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from . import FileView

        await interaction.response.send_message(
            "What file do you want to open?", ephemeral=True
        )
        filename = (
            await self.bot.wait_for(
                "message",
                check=lambda m: self.ctx.author == m.author
                and m.channel == self.ctx.channel,
            )
        ).content

        file_model = await self.bot.engine.find(
            FileModel,
            FileModel.user_id == self.ctx.author.id,
            FileModel.name == filename,
            FileModel.folder == self.path,
        )

        if not file_model:
            return await interaction.channel.send(f"{filename} doesnt exist!")

        file_model = file_model[0]
        file_ = await File.from_url(bot=self.bot, url=file_model.file_url)
        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Opened {filename}\n{''.join(['-' for _ in range(len(filename)+len('Opened '))])}\n{await get_info(file_)}",
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
        if self.file.filename in dir_files:
            return await interaction.response.send_message(
                "You can't have a file with the same name!"
            )

        file_ = FileModel(
            file_url=attachment.url,
            name=self.file.filename,
            user_id=self.ctx.author.id,
            create_epoch=int(time.time()),
            folder=self.path,
        )

        embed = EmbedFactory.ide_embed(
            self.ctx,
            f"Saved {self.file.filename}\n{''.join(['-' for _ in range(len(self.file.filename)+len('Saved '))])}\n{await get_info(attachment)}",
        )

        await interaction.response.defer()
        await self.bot.engine.save(file_)
        await self.bot_message.edit(
            embed=embed, view=FileView(self.ctx, self.file, self.bot_message)
        )
