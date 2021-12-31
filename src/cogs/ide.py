import aiohttp
import base64
import disnake
import re

from disnake.ext import commands


class EmbedFactory:
    @staticmethod
    def ide_embed(ctx: commands.Context, description: str, format_: str = "yaml") -> disnake.Embed:
        return disnake.Embed(
            title="Jarvide Text Editor",
            description=f"```{format_}\n{description}```",
            timestamp=ctx.message.created_at,
        ).set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url
        ).set_footer(
            text="The official jarvide text editor and ide. Expires in 5min"
        )

    @staticmethod
    def code_embed(ctx: commands.Context, code: str, path: str, format_: str = "py"):
        return disnake.Embed(
            title="Jarvide Text Editor",
            description=f"**{path}**\n```{format_}\n{code}```",
            timestamp=ctx.message.created_at,
        ).set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url
        ).set_footer(
            text="The official jarvide text editor and ide"
        )


class FileView(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return interaction.author == self.ctx.author and interaction.channel == self.ctx.channel

    def __init__(self, ctx, file_):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        content = await self.file.read()
        content = content.decode('utf-8')
        if len(content) < 2000:
            embed = EmbedFactory.ide_embed(self.ctx, content)
            return await interaction.response.send_message(embed=embed)

    @disnake.ui.button(label="Run", style=disnake.ButtonStyle.green)
    async def second_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.green)
    async def third_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...
    
    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green)
    async def fourth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...
    

class OpenView(disnake.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.bot = ctx.bot

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return interaction.author == self.ctx.author and interaction.channel == self.ctx.channel

    @disnake.ui.button(label="Upload", style=disnake.ButtonStyle.green)
    async def first_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        num = 0
        await interaction.response.send_message("Upload a file!", ephemeral=True)
        while not (file_ := await self.bot.wait_for('message', check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel)).attachments:
            await interaction.channel.send("Upload a file", delete_after=15)
            num += 1
            if num == 5:
                return await interaction.channel.send("Nice try. You cant break this bot!")

        file_ = file_.attachments[0]
        description = f"Opened file: {file_.filename}" \
                      f"\nType: {file_.content_type}" \
                      f"\nSize: {file_.size // 1000} KB ({file_.size:,} bytes)"
        embed = EmbedFactory.ide_embed(self.ctx, description)
        await interaction.edit_original_message(content=None, embed=embed, view=FileView(self.ctx, file_))

    @disnake.ui.button(label="Github", style=disnake.ButtonStyle.green)
    async def second_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message("Send a github repository link!", ephemeral=True)
        while True:
            url = await self.bot.wait_for("message",
                                          check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel
                                          )
            await url.edit(suppress=True)
            regex = re.compile(r"https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)"
                               r"/blob/(?P<branch>\w*)/(?P<path>[^#>]+)")
            try:
                repo, branch, path = re.findall(regex, url.content)[0]
                break
            except IndexError:
                await interaction.channel.send("Not a valid github link, please try again.")
        async with aiohttp.ClientSession() as session:
            a = await session.get(f'https://api.github.com/repos/{repo}/contents/{path}',
                                  headers={'Accept': 'application/vnd.github.v3+json'})
            content = (await a.json())["content"]
        decoded_string = base64.b64decode(content).decode("utf-8").replace("`", "`​")
        enumerated = list(enumerate(decoded_string.split("\n")))
        lines = []
        for number, line in enumerated:
            number = ("0" * (len(str(enumerated[-1][0])) - len(str(number)))) + str(number)
            line = f"\n{number} | {line}"
            lines.append(line)

        embed = EmbedFactory.code_embed(self.ctx, code="".join(lines), format_="py", path=path)
        await interaction.edit_original_message(embed=embed)

    @disnake.ui.button(label="Saved", style=disnake.ButtonStyle.green)
    async def third_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Link", style=disnake.ButtonStyle.green)
    async def fourth_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def fifth_button(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message("What would you like the filename to be?", ephemeral=True)




class Ide(commands.Cog):
    """Ide cog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ide(self, ctx: commands.Context) -> None:
        embed = EmbedFactory.ide_embed(ctx, "File open: No file currently open")
        await ctx.send(embed=embed, view=OpenView(ctx))


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""
    bot.add_cog(Ide(bot))
