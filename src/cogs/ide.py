import disnake
from disnake.ext import commands

class EmbedFactory:
    @staticmethod
    def ide_embed(ctx: commands.Context, description: str) -> disnake.Embed:
        return disnake.Embed(
                title="Jarvide Text Editor",
                description=f"```yaml\n{description}```",
                timestamp=ctx.message.created_at,
            ).set_author(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url
            ).set_footer(
                text="The official jarvide text editor and ide"
            )     

class Check:
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return interaction.author == self.ctx.author and interaction.channel == self.ctx.channel

class FileView(disnake.ui.View, Check):
    def __init__(self, ctx, file_): 
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.file = file_

    @disnake.ui.button(label="Read", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if len(await self.file.read()) < 2000:
            embed = EmbedFactory.ide_embed(self.ctx, await self.file.read())
            return await interaction.response.send_message(embed=embed)
        
class OpenView(disnake.ui.View, Check):
    def __init__(self, ctx): 
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot

    @disnake.ui.button(label="Upload", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):  
        num = 0
        await interaction.response.send_message("Upload a file", ephemeral=True)
        while not (file_ := await self.bot.wait_for('message', check=lambda m: self.ctx.author == m.author and m.channel == self.ctx.channel)).attachments:
            await interaction.channel.send("Upload a file", delete_after=15)
            num += 1
            if num == 5:
                return await interaction.channel.send("Nice try. You cant break this bot!")
        
        file_ = file_.attachments[0]

        embed = EmbedFactory.ide_embed(self.ctx, f"Opened file: {file_.filename}")
        await interaction.edit_original_message(embed=embed, view=FileView(self.ctx, file_))

    @disnake.ui.button(label="Github", style=disnake.ButtonStyle.green)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...
    
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

    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.red)
    async def fifth_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        ...
    

class StartView(disnake.ui.View, Check):
    def __init__(self, ctx):
        super().__init__()

        self.ctx = ctx

    @disnake.ui.button(label="Open", style=disnake.ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        
        embed = EmbedFactory.ide_embed(self.ctx, "How would you like to open your file?")

        await interaction.response.defer()
        await interaction.edit_original_message(embed=embed, view=OpenView(self.ctx))
    



class Ide(commands.Cog):
    """Ide cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def ide(self, ctx: commands.Context) -> None:
        embed = EmbedFactory.ide_embed(ctx, "No file currently open")
        await ctx.send(embed = embed, view=StartView(ctx))

    


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""

    bot.add_cog(Ide(bot))
