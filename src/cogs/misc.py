import disnake

from disnake.ext import commands


class Misc(commands.Cog):
    """
    Misc cog for randomly assorted commands that don't fall into
    any specific category.
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["latency"])
    async def ping(self, ctx: commands.Context):
        if round(self.bot.latency * 1000) > 150:
            health, color = "Unhealthy", disnake.Color.red()
        elif round(self.bot.latency * 1000) in range(90, 150):
            health, color = "Almost unhealthy", disnake.Color.yellow()
        elif round(self.bot.latency * 1000) in range(55, 90):
            health, color = "Healthy", disnake.Color.green()
        else:
            health, color = "Very Healthy", 0x90EE90

        embed = (
            disnake.Embed(color=color)
            .add_field(
                name="**Roundtrip**",
                value=f"```{round(self.bot.latency * 1000)} ms```"
                )
            .add_field(name="**Health**", value=f"```{health}```")
            .set_footer(
                text="Discord API issues could lead to high roundtrip times"
                )
            )
        await ctx.send(content="🏓**Pong**", embed=embed)


def setup(bot: commands.Bot) -> None:
    """Setup misc cog"""
    bot.add_cog(Misc(bot))
