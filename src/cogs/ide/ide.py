import copy

import disnake

from .dialogs import OpenView
from src.utils import EmbedFactory
from disnake.ext import commands, tasks

from typing import Optional


class Ide(commands.Cog):
    """Ide cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_commands = {}
        self.check_activity.start()

    @tasks.loop(seconds=1)
    async def check_activity(self):
        for channel in copy.copy(self.active_commands):
            for user in copy.copy(self.active_commands[channel]):
                message = self.bot.get_message(self.active_commands[channel][user])
                if not message:
                    del self.active_commands[channel][user]
                    return
                if all(all(k.disabled for k in child.children if isinstance(k, disnake.ui.Button))
                       for child in message.components if isinstance(child, disnake.ActionRow)):
                    del self.active_commands[channel][user]

    @commands.command(
        help="""Have you used the linux commandline editor, nano? This discord text editor is like nano , and implements safe, reliable and fast file storing with editing and compiling technology. The database is secure and cannot be accessed or broken into by anyone, not even the core developers. You can upload or create files and these files would be saved into a filesystem which you can open at any time. If you have an open file you can compile it and run it (depending on the filetype). You can also edit the content and replace text. You can also pull and push to github depending on the file/folder you uploaded."""
    )
    async def ide(
        self, ctx: commands.Context, query: str = None, link: str = None
    ) -> Optional[disnake.Message]:
        if (
            ctx.channel in self.active_commands
            and ctx.author in self.active_commands[ctx.channel]
        ):
            return await ctx.send(
                "You already have an open ide in this channel! Press the `exit` button to make a new one!",
                delete_after=15
            )

        embed = EmbedFactory.ide_embed(ctx, "File open: No file currently open")
        view = OpenView(ctx)
        view.bot_message = await ctx.send(
            embed=embed,
            view=view,
        )

        if ctx.channel not in self.active_commands:
            self.active_commands[ctx.channel] = {}
        self.active_commands[ctx.channel][ctx.author] = view.bot_message.id


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""
    bot.add_cog(Ide(bot))
