

from disnake import (
    Embed, 
    Member
)
from disnake.ext.commands import (
    Cog,
    CooldownMapping, 
    BucketType,
    Context,
    command
)
from ..bot import Jarvide
    
class Image(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """
    Imagine yourself in prison...this image manipulation cog makes dreams reality!
    """

    def __init__(self, bot: Jarvide) -> None:
        self.bot = bot  

        self.emoji = "🖼️"
        self.short_help_doc = "Awesome image manipulation"


    @staticmethod
    async def overlay(ctx: Context, endpoint: str, member: Member = None) -> None:
        """Shortcut method for sending image"""

        member = member or ctx.author
        await ctx.send(
            embed=Embed(color=0x90EE90)
            .set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            .set_image(
                url=f"https://some-random-api.ml/canvas/{endpoint}?avatar={member.avatar.with_format('png').url}"
            )
        )

    @command()
    async def gay(self, ctx: Context, member: Member = None):
        """Gay'ify a profile picture!"""

        await self.overlay(ctx, "gay", member)

    @command()
    async def wasted(self, ctx: Context, member: Member = None):
        """Waste'tify a profile picture!"""

        await self.overlay(ctx, "wasted", member)

    @command()
    async def jail(self, ctx: Context, member: Member = None):
        """Jail'ify a profile picture!"""

        await self.overlay(ctx, "jail", member)

    @command()
    async def triggered(self, ctx: Context, member: Member = None):
        """Trigger'ify a profile picture!"""

        await self.overlay(ctx, "triggered", member)


def setup(bot: Jarvide) -> None:
    bot.add_cog(Image(bot))