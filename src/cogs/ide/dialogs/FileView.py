import disnake

from src.utils import *
from .EditView import EditView


class FileView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx, file_: File, bot_message: disnake.Message = None):
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
        content = add_lines(self.file.content)
        if len("".join(content)) < 2000:
            embed = EmbedFactory.ide_embed(
                self.ctx, "".join(content), format_=self.extension
            )
            return await interaction.response.send_message(embed=embed)

        await LinePaginator(
            interaction,
            [line.strip("\n") for line in content],
            prefix=f"```{self.extension}",
            suffix="```",
            line_limit=50,
            timeout=None,
            embed_author_kwargs={
                'name': f"{self.ctx.author.name}'s automated paginator for {self.file.filename}.",
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
                timeout=None,
                embed_author_kwargs={
                'name': f"{self.ctx.author.name}'s automated paginator for {self.file.filename}.",
                'icon_url': self.ctx.author.avatar.url
            }
            ).start()

        await self.bot_message.edit(
            embed=EmbedFactory.code_embed(
                self.ctx, "".join(add_lines(content)), self.file.filename
            ),
            view=EditView(self.ctx, self.file, self.bot_message),
        )
        
