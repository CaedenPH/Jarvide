from .dialogs import OpenView
from src.utils import EmbedFactory
from disnake.ext import commands


class Ide(commands.Cog):
    """Ide cog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def ide(self, ctx: commands.Context) -> None:
        embed = EmbedFactory.ide_embed(ctx, "File open: No file currently open")
        view = OpenView(ctx)
        view.bot_message = await ctx.send(embed=embed, view=view)


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""
    bot.add_cog(Ide(bot))
