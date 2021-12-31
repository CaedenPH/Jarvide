import disnake

from disnake.ext import commands


class Misc(commands.Cog):
    """Misc cog for randomly assorted commands that dont fall into any specific category."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        if round(self.bot.latency * 1000) > 150:
            health = "Unhealthy"
            color = disnake.Color.red()
        elif round(self.bot.latency * 1000) in range(70, 148):
            health = "Unhealthy"
            color = disnake.Color.yellow()
        else:
            health = "Healthy"
            color = disnake.Color.green()

        embed = disnake.Embed(
            color=color
        ).add_field(
            name="**Roundtrip**",
            value=f"```{round(self.bot.latency * 1000)} ms```"
        ).add_field(
            name="**Health**",
            value=f"```{health}```"
        ).set_footer(
            text="Discord API issues could lead to high roundtrip times"
        )
        await ctx.send(content="🏓**Pong**", embed=embed)


def setup(bot: commands.Bot) -> None:
    """Setup misc cog"""
    bot.add_cog(Misc(bot))
