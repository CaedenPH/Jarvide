import disnake
import traceback

from disnake.ext import commands
import datetime
from typing import Optional
import difflib

from disnake.ext.commands.errors import MissingRequiredArgument

def underline(text, at, for_):
            import itertools
            underline = "".join(itertools.repeat(" ", at)) + "".join(itertools.repeat("^", for_))
            return text + "\n" + underline

class SupportServerView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(disnake.ui.Button(label = f"Click to join our support server...", url = "https://discord.gg/3rCjFkqq"))


async def send_error(
    ctx: commands.Context,
    error: str,
    errororiginal
) -> None:
    if isinstance(errororiginal, commands.MissingRequiredArgument):
        aliases = ctx.command.aliases
        aliases.append(ctx.command.name)
        desc = f"```\n{ctx.prefix}[{'/'.join(aliases)}] {ctx.command.signature}\n```"
        desc = underline(desc, desc.index(f"<{errororiginal.param}>", len(f"<{errororiginal.param}")))
        emb = disnake.Embed(title = f"You missed a required argument <{errororiginal.param}>", description = f"```\n{desc}\n```")    
        return await ctx.send(embed=emb)
    elif isinstance(errororiginal, commands.CommandNotFound):
        results = []
        cmd = ctx.message.split(ctx.prefix)[0]
        for i in ctx.bot.commands:
            if len(difflib.get_close_matches(cmd, i.name)) > 0:
                results.append(f"- `{i.name}`\n")
        emb = disnake.Embed(title = f"No such a command!", description = f"This command doesnt even exist! Perhaps you meat any of those?\n{''.join(results)}")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.DisabledCommand):
        emb = disnake.Embed(title = f"Command disabled..", description = f"{ctx.commane.name} is currently disabled... If you think this is a mistake, please contact our support server by clicking the button bellow")
        await ctx.send(embed = emb, view = SupportServerView())
    elif isinstance(errororiginal, commands.TooManyArguments):
        aliases = ctx.command.aliases
        aliases.append(ctx.command.name)
        desc = f"```\n{ctx.prefix}[{'/'.join(aliases)}] {ctx.command.signature}\n```"
        emb = disnake.Embed(title = f"Too many args!", description = f"You passed more arguments than expected, ```yaml\nusage: {desc}\n```")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.CommandOnCooldown):
        emb = disnake.Embed(title = f"Woah calm down..", description = f"This command has a cooldown of {errororiginal.rate} uses per {datetime.timedelta(seconds=errororiginal.per)}, you may retry in {datetime.timedelta(seconds=error.retry_after)}")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.NotOwner):
        emb = disnake.Embed(title = f"You are not the owner to do this!", description = f"This command is for the owner only, you may not use it!")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.MessageNotFound):
        sendtochannel = True
    elif isinstance(errororiginal, commands.MemberNotFound):
        emb = disnake.Embed(title = f"No such a member!", description = f"The member {errororiginal.argument} doesnt exist in this guild, maybe he is not in this guild.")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.UserNotFound):
        emb = disnake.Embed(title = f"This user doesnt exist", description = f"The user {errororiginal.argument} doesnt exist in the bot's cache or doesnt exist at all!")
        await ctx.send(embed = emb)            
    elif isinstance(errororiginal, commands.ChannelNotFound):
        emb = disnake.Embed(title = f"This channel is not in this guild/doesnt exist", description = f"Channel {errororiginal.argumen} doesnt exist or is not in this guild.")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.MissingPermissions):
        emb = disnake.Embed(title = f"No permissions...", description = f"You are missing the {' '.join((errororiginal.missing_permissions)} permissions to perform this command...")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.BotMissingPermissions):
        emb = disnake.Embed(title = "I Am missing permissions to do this...", description = f"I Do not have the {' '.join(errororiginal.missing_permissions)} permission to do this...")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.MissingRole):
        emb = disnake.Embed(title = f"This command is for a specific role!", description = f"This command is only for the role {errororiginal.missing_role.mention}, and you cant perform it since you dont have it!")
        await ctx.send(embed = emb)
    elif isinstance(errororiginal, commands.ExtensionFailed):
        sendtochannel = True            
    else:
        sendtochannel = True
    if sendtochannel:
        channel = ctx.bot.get_channel(927596019468873748)
        _traceback = traceback.format_exception(
            type(errororiginal),
            errororiginal,
            errororiginal.__traceback__
            )
        emb = disnake.Embed(
            title=f"Error by {ctx.author} at {ctx.message.created_at}",
            description=(
                f"**info**\n> **error**: {error}\n> " +
                f"**cog**: {ctx.command.cog_name}\n" +
                f"**command**: {ctx.command.name}\n" +
                f"**traceback**\n```py\n{_traceback}\n```"
                ), 
            color = disnake.Colour.red()
        )
        await channel.send(embed=emb)
        emb = disnake.Embed(title = f"Oops! Something went wrong...", description = f"Something went wrong while trying to run your command... If you think this is a mistake, please contact the developers in our discord server [here](https://discord.gg/3rCjFkqq)", color = disnake.Colour.red())
        return await ctx.send(embed = emb, view = SupportServerView())
    
class Error(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        err: Optional[commands.MissingRequiredArgument]
    ):
        await send_error(ctx, err, err)


def setup(bot):
    bot.add_cog(Error(bot))
