import disnake
import traceback
from disnake.ext import commands

async def error(ctx, error, errororiginal, sendtochannel):
    if sendtochannel == True:
        channel = ctx.bot.get_channel(927596019468873748)
        _traceback = traceback.format_exception(type(errororiginal), errororiginal, errororiginal.__traceback__)
        emb = disnake.Embed(
            title = f"Error by {ctx.author} at {ctx.message.created_at}", description = f"**info**\n> **error**: {error}\n> **cog**: {ctx.command.cog_name}\n**command**: {ctx.command.name}\n**traceback**\n```py\n{_traceback}\n```"
        )
        await channel.send(embed = emb)
        

class Error(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await error(ctx, "TEST", error, True)


def setup(bot):
    bot.add_cog(Error(bot))        
