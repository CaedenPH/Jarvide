import disnake

from disnake.ext import commands


class Staff(commands.Cog, command_attrs={"hidden": True}):
    """Staff cog for only staff members to use."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def load(self, ctx: commands.Context, extension: str):
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        self.bot.load_extension(f"src.cogs.{extension}")
        embed.add_field(
            name="Load Extension", value=f"Loaded cog: ``{extension}`` successfully"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def unload(self, ctx: commands.Context, extension: str):
        self.bot.unload_extension(f"src.cogs.{extension}")
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        embed.add_field(
            name="Unload Extension", value=f"Unloaded cog: ``{extension}`` successfully"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["re"])
    async def reload(self, ctx: commands.Context, extension: str = None):
        if not extension:
            for cog in tuple(self.bot.extensions):
                self.bot.reload_extension(cog)
            embed = disnake.Embed(color=disnake.Color.dark_gold())
            embed.add_field(
                name="Reload Extension", value=f"Reloaded cogs successfully"
            )
            print("----------------------------------------")
            return await ctx.send(embed=embed)

        print("----------------------------------------")
        self.bot.reload_extension(f"cogs.{extension}")
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        embed.add_field(
            name="Reload Extension", value=f"Reloaded cog: ``{extension}`` successfully"
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Setup staff cog"""
    bot.add_cog(Staff(bot))
