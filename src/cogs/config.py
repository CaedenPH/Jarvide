import disnake

from disnake.ext.commands import (
    Cog, 
    BucketType, 
    CooldownMapping,
    Bot, 
    Context, 
    command,
    has_permissions
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
    

    @command(aliases=[
        'removeconfig',
        'rconfig',
        'deleteconfig',
        'delconfig',
        'removeconf',
    ])
    @has_permissions(
        manage_guild=True,
    )
    async def remove_config(self, ctx: Context): 
        #TODO: database remove_config shit here for auto_calc
        ...





def setup(bot: Bot):
    bot.add_cog(Config(bot))