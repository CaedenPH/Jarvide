import disnake
from disnake.permissions import P

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
        self.bot_message = bot_message

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = add_lines(self.file.content)
        if len(content) < 2000:
            embed = EmbedFactory.ide_embed(self.ctx, content, format_=self.file.filename.split('.')[-1])
            return await interaction.response.send_message(embed=embed)

        await TextPaginator(interaction, content).start()

    @disnake.ui.button(label="Run", style=disnake.ButtonStyle.green)
    async def second_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = self.file.content
        name = self.file.filename.split(".")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://emkc.org/api/v1/piston/execute",
                    json={"language": name[-1], "source": content},
            ) as data:
                
                json = await data.json()
                print(json)

            await TextPaginator(interaction, f"```yaml\n{json['output']}```").start()

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.green)
    async def third_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        content = add_lines(self.file.content)
        if len(content) < 4000:
            return await self.bot_message.edit(
                embed=EmbedFactory.code_embed(self.ctx, content, self.file.filename),
                view=EditView(self.ctx, self.file, self.bot_message)
            )  
        await TextPaginator(interaction, content).start()