from disnake import Member, Color, Embed
import async_cse
import random


from ..HIDDEN import KEY
from disnake.ext.commands import (
    Cog, 
    BucketType, 
    CooldownMapping, 
    Bot, 
    Context, 
    command
)

from ..bot import Jarvide
from ..utils.utils import EmbedFactory

bug_string = """
Thank you for reporting a bug! My team will work hard to solve this!


My team might want to ask you some questions, so we would love you to keep dm's open or join our support server!
[ discord.gg/mtue4UnWaA ]
-----------------------------------------------------------
Bug id: {}"""


class Misc(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """
    Miscellaneous category for randomly assorted commands that don't fall into any specific category.
    """

    def __init__(self, bot: Jarvide) -> None:
        self.bot = bot

        self.emoji = "🌀"
        self.short_help_doc = "Commands which don't fit anywhere else."
        self.google = async_cse.Search(KEY)

    @command(name="google", aliases=["g"])
    async def google(self, ctx: Context, *, query: str):
        """Search stuff up on google!"""

        try:
            results = await self.google.search(query, safesearch=True, image_search=False)
        except async_cse.NoResults:
            return await ctx.send(f"No **Results** found for search **{query}**")
        if not results:
            return await ctx.send(f"No **Results** found for search **{query}**")

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

    @command(aliases=["latency"])
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

    @command(aliases=["bug", "broken"])
    async def report(self, ctx: Context):
        """Found a bug? Report it!"""

        responses = []
        for iteration, question in enumerate(
            [
                "sum up your report in less than 10 words",
                "explain your report. present as detailed of a description as you can provide, including button clicks, errors shown (if any), file open, and intention",
            ],
            start=1,
        ):
            await ctx.send(
                f"Please {question}\nType q to end your report\nQuestion number {iteration}/2"
            )

            message = await self.bot.wait_for(
                "message",
                timeout=560,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if message.content.lower() == "q":
                return

            responses.append(message.content)

        embed = Embed(
            title=responses[0],
            description="```yaml\n" + responses[0] + "```",
            timestamp=ctx.message.created_at,
        ).set_author(name=f"From {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await self.bot.report_channel.send(embed=embed)
        bug_id = random.choice(self.bot.bugs)

        embed = EmbedFactory.ide_embed(ctx, bug_string.format(bug_id))
        await ctx.send(embed=embed)


def setup(bot: Jarvide) -> None:
    bot.add_cog(Misc(bot))
