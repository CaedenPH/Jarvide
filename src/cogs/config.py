import disnake

from disnake.ext.commands import (
    Cog,
    BucketType,
    CooldownMapping,
    Bot,
    Context,
    command,
    has_permissions,
)


class Config(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """
    Miscellaneous category for randomly assorted commands that don't fall into any specific category.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.ignore = True
        self.detectors = ["calc", "github", "file", "codeblock"]

    @command(
        aliases=[
            "removeconfig",
            "rconfig",
            "deleteconfig",
            "delconfig",
            "removeconf",
        ]
    )
    @has_permissions(
        manage_guild=True,
    )
    async def remove_config(self, ctx: Context, auto: str = None):
        embed = disnake.Embed(title="Uh oh", description="").set_author(
            name=ctx.author.name, icon_url=ctx.author.avatar.url
        )

        if not (auto in self.detectors):
            embed.description = f"There are no autodetections called: {auto}\nThe current detections are `{', '.join(self.detectors)}`"
            return await ctx.send(embed=embed)

    @command(
        aliases=[
            "createconfig",
            "newconfig",
            "makeconfig",
            "cconfig",
            "createconf",
        ]
    )
    @has_permissions(
        manage_guild=True,
    )
    async def create_config(self, ctx: Context, auto: str = None):
        ...
        # TODO: data


def setup(bot: Bot):
    bot.add_cog(Config(bot))
