import disnake
from disnake.ext import commands

class Staff(commands.Cog):
    """Staff cog for only staff members to use."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, extension):
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        self.bot.load_extension(f'cogs.{extension}')
        embed.add_field(name="Load Extension", value=f"Loaded cog: ``{extension}`` successfully")
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, extension):
            self.bot.unload_extension(f'cogs.{extension}')
            embed = disnake.Embed(color=disnake.Color.dark_gold())
            embed.add_field(name="Unload Extension", value=f"Unloaded cog: ``{extension}`` successfully")
            await ctx.send(embed=embed)

    @commands.command(aliases=['r'], hidden=True)
    async def reload(self, ctx: commands.Context, extension=""):
        if not extension:
            for cog in tuple(self.bot.extensions):
                if cog[5:] not in ["Misc", "Economy", "Mod"]:
                    self.bot.reload_extension(cog)
            embed = disnake.Embed(color=disnake.Color.dark_gold())
            embed.add_field(name="Reload Extension", value=f"Reloaded cogs successfully")
            print('\n\n\n\nReloaded\n--------------------------------')
            return await ctx.send(embed=embed)
            
        self.bot.reload_extension(f'cogs.{extension}')
        embed = disnake.Embed(color=disnake.Color.dark_gold())
        embed.add_field(name="Reload Extension", value=f"Reloaded cog: ``{extension}`` successfully")
        await ctx.send(embed=embed)    

def setup(bot: commands.Bot) -> None:
    """Setup staff cog"""

    bot.add_cog(Staff(bot))
