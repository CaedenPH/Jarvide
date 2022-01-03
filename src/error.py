import disnake
import traceback

from disnake.ext import commands
from typing import Optional

async def error(
    ctx: commands.Context,
    error: str,
    errororiginal: commands.MissingRequiredArgument,
    sendtochannel: bool
    ) -> None:
    if sendtochannel == True:
        channel = ctx.bot.get_channel(927596019468873748)
        _traceback = traceback.format_exception(
            type(errororiginal),
            errororiginal,
            errororiginal.__traceback__
            )
        emb = disnake.Embed(
            title = f"Error by {ctx.author} at {ctx.message.created_at}",
            description = (
                f"**info**\n> **error**: {error}\n> " +
                f"**cog**: {ctx.command.cog_name}\n" +
                f"**command**: {ctx.command.name}\n" +
                f"**traceback**\n```py\n{_traceback}\n```"
                )
        await channel.send(embed = emb)


class Error(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        err: Optional[commands.MissingRequiredArgument]
        ):
        if isinstance(err, commands.MissingRequiredArgument):
            await error(ctx, "TEST", err, True)


def setup(bot):
    bot.add_cog(Error(bot))
