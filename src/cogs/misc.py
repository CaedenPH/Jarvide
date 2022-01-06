from disnake import Member, Color, Embed
import aiohttp
import async_cse


from ..HIDDEN import KEY
from disnake.ext.commands import Cog, BucketType, CooldownMapping, Bot, Context, command


class Misc(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """
    Miscellaneous category for randomly assorted commands that don't fall into any specific category.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.emoji = "🌀"
        self.short_help_doc = "Commands which don't fit anywhere else."
        self.google = async_cse.Search(KEY)

    @staticmethod
    async def overlay(ctx: Context, endpoint: str, member: Member = None) -> None:
        """Shortcut method"""
        member = member or ctx.author
        await ctx.send(
            embed=Embed(color=0x90EE90)
            if member is None:
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            else:
                embed.set_author(name=member, icon_url=member.avatar.url)
            .set_image(
                url=f"https://some-random-api.ml/canvas/{endpoint}?avatar={member.avatar.with_format('png').url}"
            )
        )

    @command(name="google", aliases=["g"])
    async def google(self, ctx: Context, *, query: str):
        """Search stuff up on google!"""
        results = await self.google.search(query, safesearch=True, image_search=False)
        if not results:
            return await ctx.send("No Results Found")

        await ctx.send(
            embed=Embed(
                title=f"Query: {query}",
                description="\n".join(
                    [
                        f"[{res.title}]({res.url})\n{res.description}\n\n"
                        for res in results[:5]
                    ]
                ),
                color=0x489CC4,
            )
            .set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )
            .set_author(
                name=ctx.author,
                icon_url="https://staffordonline.org/wp-content/uploads/2019/01/Google.jpg",
            )
        )

    @command()
    async def ping(self, ctx: Context):
        """Returns Jarvide's latency."""
        if round(self.bot.latency * 1000) > 150:
            health, color = "Unhealthy", Color.red()
        elif round(self.bot.latency * 1000) in range(90, 150):
            health, color = "Almost unhealthy", Color.yellow()
        elif round(self.bot.latency * 1000) in range(55, 90):
            health, color = "Healthy", Color.green()
        else:
            health, color = "Very Healthy", 0x90EE90

        embed = (
            Embed(color=color)
            .add_field(
                name="**Roundtrip**", value=f"```{round(self.bot.latency * 1000)} ms```"
            )
            .add_field(name="**Health**", value=f"```{health}```")
            .set_footer(text="Discord API issues could lead to high roundtrip times")
        )
        await ctx.send(content="🏓**Pong**", embed=embed)

    @command()
    async def roast(self, ctx: Context, *, member: Member):
        """Roast someone!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://evilinsult.com/generate_insult.php?lang=en&type=json"
            ) as resp:
                await ctx.send(
                    member.mention,
                    embed=Embed(
                        description=(await resp.json())["insult"], color=0x90EE90
                    ),
                )

    @command()
    async def gay(self, ctx: Context, *, member: Member = None):
        """Gay'ify a profile picture!"""
        await self.overlay(ctx, "gay", member)

    @command()
    async def wasted(self, ctx: Context, *, member: Member = None):
        """Waste'tify a profile picture!"""
        await self.overlay(ctx, "wasted", member)

    @command()
    async def jail(self, ctx: Context, *, member: Member = None):
        """Jail'ify a profile picture!"""
        await self.overlay(ctx, "jail", member)

    @command()
    async def triggered(self, ctx: Context, *, member: Member = None):
        """Trigger'ify a profile picture!"""
        await self.overlay(ctx, "triggered", member)


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
