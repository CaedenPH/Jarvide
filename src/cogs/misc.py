import disnake
import aiohttp
import random
import async_cse


from ..HIDDEN import KEY
from disnake.ext import commands


class Misc(
    commands.Cog,
    command_attrs={
        "cooldown": commands.CooldownMapping.from_cooldown(
            1, 3.5, commands.BucketType.user5
        )
    },
):
    """
    Misc cog for randomly assorted commands that don't fall into any specific category.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🌀"
        self.short_help_doc = "Commands which don't fit anywhere else"
        self.google = async_cse.Search(KEY)

    async def overlay(
        self, ctx: commands.Context, endpoint: str, member: disnake.Member = None
    ) -> disnake.Message:
        """Shortcut method"""
        member = member or ctx.author
        await ctx.send(
            embed=disnake.Embed(color=0x90EE90)
            .set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            .set_image(
                url=f"https://some-random-api.ml/canvas/{endpoint}?avatar={member.avatar.with_format('png').url}"
            )
        )

    @commands.command(name="google", aliases=["find", "gsearch"])
    async def google(self, ctx: commands.Context, *, query: str):
        """Search stuff up on google"""
        results = await self.google.search(query, safesearch=True, image_search=False)
        if not results:
            return await ctx.send_error("No Results Found")

        await ctx.send(
            embed=disnake.Embed(
                title=f"Query: {query}",
                description="\n".join(
                    [
                        f"[{res.title}]({res.url})\n{res.description}\n\n"
                        for res in results[:5]
                    ]
                ),
                color=self.bot.ok_color,
            )
            .set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar
            )
            .set_author(
                name=ctx.author,
                icon_url="https://staffordonline.org/wp-content/uploads/2019/01/Google.jpg",
            )
        )

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Returns Jarvide's latency"""
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
                name="**Roundtrip**", value=f"```{round(self.bot.latency * 1000)} ms```"
            )
            .add_field(name="**Health**", value=f"```{health}```")
            .set_footer(text="Discord API issues could lead to high roundtrip times")
        )
        await ctx.send(content="🏓**Pong**", embed=embed)

    @commands.command()
    async def roast(self, ctx: commands.Context, *, member: disnake.Member):
        """Roast someone or sum shit. idk"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://evilinsult.com/generate_insult.php?lang=en&type=json"
            ) as resp:
                await ctx.send(
                    member.mention,
                    embed=disnake.Embed(
                        description=(await resp.json())["insult"], color=0x90EE90
                    ),
                )

    @commands.command()
    async def gay(self, ctx, *, member: disnake.Member = None):
        """Gay overlay"""
        await self.overlay(ctx, "gay", member)

    @commands.command()
    async def wasted(self, ctx, *, member: disnake.Member = None):
        """Wasted overlay"""
        await self.overlay(ctx, "wasted", member)

    @commands.command()
    async def passed(self, ctx, *, member: disnake.Member = None):
        """Passed overlay"""
        await self.overlay(ctx, "passed", member)

    @commands.command()
    async def jail(self, ctx, *, member: disnake.Member = None):
        """Jail overlay"""
        await self.overlay(ctx, "jail", member)

    @commands.command()
    async def comrade(self, ctx, *, member: disnake.Member = None):
        """Comrade overlay"""
        await self.overlay(ctx, "comrade", member)

    @commands.command()
    async def triggered(self, ctx, *, member: disnake.Member = None):
        """Triggered overlay"""
        await self.overlay(ctx, "triggered", member)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
