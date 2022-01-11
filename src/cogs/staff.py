import disnake

from disnake.ext.commands import Cog, Context, Bot, command


class Staff(Cog, command_attrs={"hidden": True}):
    """Staff cog for only staff members to use."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @command()
    async def load(self, ctx: Context, extension: str):
        """Load an extension."""
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        self.bot.load_extension(f"src.cogs.{extension}")
        embed.add_field(
            name="Extension Loaded", value=f"Loaded cog `{extension}` successfully!"
        )
        await ctx.send(embed=embed)

    @command()
    async def unload(self, ctx: Context, extension: str):
        """Unload an extension."""

        self.bot.unload_extension(f"src.cogs.{extension}")
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        embed.add_field(
            name="Extension Unloaded", value=f"Unloaded cog `{extension}` successfully!"
        )
        await ctx.send(embed=embed)

    @command(aliases=["re"])
    async def reload(self, ctx: Context, extension: str = None):
        """Reload all the extensions in the bot."""
        if not extension:
            for cog in tuple(self.bot.extensions):
                self.bot.reload_extension(cog)
            embed = disnake.Embed(color=disnake.Color.dark_gold())
            embed.add_field(
                name="Extensions Reloaded", value="Reloaded cogs successfully."
            )
            return await ctx.send(embed=embed)

        self.bot.reload_extension(f"cogs.{extension}")
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        embed.add_field(
            name="Extension Reloaded", value=f"Reloaded cog `{extension}` successfully!"
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Staff(bot))
