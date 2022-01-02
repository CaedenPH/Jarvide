import disnake
import aiohttp

from src.utils import File, add_lines, EmbedFactory, LinePaginator, TextPaginator, get_info
from .EditView import EditView


class FileView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx, file_: File, bot_message: disnake.Message):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_
        self.extension = file_.filename.split(".")[-1]
        self.bot_message = bot_message

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        content = add_lines(self.file.content)
        if len("".join(content)) < 2000:
            embed = EmbedFactory.ide_embed(
                self.ctx, "".join(content), format_=self.extension
            )
            return await self.bot_message.edit(embed=embed)

        await LinePaginator(
            interaction,
            [line.strip("\n") for line in content],
            prefix=f"```{self.extension}",
            suffix="```",
            line_limit=50,
            timeout=None,  # type: ignore
            embed_author_kwargs={
                'name': f"{self.ctx.author.name}'s automated paginator for {self.file.filename}",
                'icon_url': self.ctx.author.avatar.url
            }
        ).start()

    @disnake.ui.button(label="Run", style=disnake.ButtonStyle.green)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = self.file.content
        name = self.extension

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://emkc.org/api/v1/piston/execute",
                json={"language": name, "source": content},
            ) as data:

                json = await data.json()
                if 'message' in json and 'runtime is unknown' in json['message']:
                    await interaction.response.defer()
                    return await interaction.channel.send("This file has an invalid file extension and therefore I do not know what language to run it in! Try renaming your file", delete_after=15)
                
                output = json['output']

                if not output:
                    output = "[No output]"

            await TextPaginator(interaction, f"```yaml\n{output}```").start()

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.green)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        content = self.file.content
        if len(content) > 4000:
            return await LinePaginator(
                interaction,
                [line.strip("\n") for line in content],
                prefix=f"```{self.extension}",
                suffix="```",
                line_limit=60,
                timeout=None,  # type: ignore
                embed_author_kwargs={
                    'name': f"{self.ctx.author.name}'s automated paginator for {self.file.filename}",
                    'icon_url': self.ctx.author.avatar.url
                }
            ).start()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx, "".join(add_lines(content)), self.file.filename
            ),
            view=EditView(self.ctx, self.file, self.bot_message, self),
        )

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
        file_ = File(filename=filename, content=self.file.content, bot=self.bot)
        description = await get_info(file_)

        self.file = file_
        self.extension = file_.filename.split(".")[-1]

        embed = EmbedFactory.ide_embed(self.ctx, description)
        await self.bot_message.edit(embed=embed)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.red)
    async def back_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        from .OpenView import OpenView

        await interaction.response.defer()
        await self.bot_message.edit(
            embed=EmbedFactory.ide_embed(self.ctx, "File open: No file currently open"),
            view=OpenView(self.ctx, self.bot_message)
        )
