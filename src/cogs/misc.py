import disnake
import aiohttp
import random
import async_cse

from ..HIDDEN import KEY
from disnake.ext import commands


class Misc(commands.Cog):
    """
    Misc cog for randomly assorted commands that don't fall into any specific category.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = '🌀'
        self.short_help_doc = 'Commands which don\'t fit anywhere else'
        self.google = async_cse.Search(KEY)
    
    # embed 
    async def overlay(
        self, ctx: commands.Context, endpoint: str, member: disnake.Member = None
    ):
        member = member or ctx.author
        emb = disnake.Embed(color=0x90EE90).set_image(
            url=f"https://some-random-api.ml/canvas/{endpoint}?avatar={member.avatar.with_format('png').url}"
            )
        emb.set_author(name=ctx.author, icon_url=str(ctx.author.avatar))
        await ctx.send(embed=emb)

    @commands.command(name="google", aliases=["find", "search"])
    async def google(self, ctx, *, query):
        # google command
        safesearch = True
        if isinstance(ctx.channel, disnake.TextChannel):
            safesearch = not ctx.channel.is_nsfw()
        try:
            response = await self.google.search(query, safesearch=safesearch)

        except async_cse.search.NoResults:
            await ctx.reply(f"Woops, no results found for `{query}`!")
            return

        if len(response) == 0:
            await ctx.reply_embed(f"Woops, no results found for `{query}`!")
            return

        embed = disnake.Embed(
            color=0x00A6F2,
            title=response[0].title,
            description=response[0].description,
            url=response[0].url,
        )
        await ctx.reply(embed=embed, mention_author=False)
    
    # get bot latency 
    @commands.command()
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
                name="**Roundtrip**", value=f"```{round(self.bot.latency * 1000)} ms```"
            )
            .add_field(name="**Health**", value=f"```{health}```")
            .set_footer(text="Discord API issues could lead to high roundtrip times")
        )
        await ctx.send(content="🏓**Pong**", embed=embed)
    
    # roasts...someone?
    @commands.command()
    async def roast(self, ctx: commands.Context, *, member: disnake.Member):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://evilinsult.com/generate_insult.php?lang=en&type=json"
            ) as res:
                resp = await res.json()
                insult = resp["insult"]
                color = 0x90EE90
                embed = disnake.Embed(color=color, description=insult)
                await ctx.send(f"{member.mention}", embed=embed)
    
    # gets a random meme
    @commands.command()
    async def meme(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://reddit.com/r/dankmemes.json?sort=hot") as resp:
                _json = await resp.json()
                color = 0x90EE90
                post = random.choice(_json["data"]["children"])["data"]
                embed = disnake.Embed(
                    color=color, title=post["title"], url=post["permalink"]
                ).set_image(url=post["url"])
                await ctx.send(embed=embed)

    # gets a reddit post
    @commands.command()
    async def reddit(self, ctx: commands.Context, subreddit: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                f"https://reddit.com/r/{subreddit}.json?sort=hot"
            ) as resp:
                _json = await resp.json()
                post = random.choice(_json["data"]["children"])["data"]
                if "url" in post:
                    embed = (
                        disnake.Embed(
                            color=0x90EE90, title=post["title"], url=post["permalink"]
                        )
                    ).set_image(url=post["url"])
                else:
                    embed = disnake.Embed(
                        color=0x90EE90,
                        title=post["title"],
                        url=post["permalink"],
                        description=post["selftext"],
                    )

                await ctx.send(embed=embed)
    
    # random stuff
    @commands.command()
    async def gay(self, ctx, *, member: disnake.Member = None):
        await self.overlay(ctx, "gay", member)

    @commands.command()
    async def wasted(self, ctx, *, member: disnake.Member = None):
        await self.overlay(ctx, "wasted", member)

    @commands.command()
    async def passed(self, ctx, *, member: disnake.Member = None):
        await self.overlay(ctx, "passed", member)

    @commands.command()
    async def jail(self, ctx, *, member: disnake.Member = None):
        await self.overlay(ctx, "jail", member)

    @commands.command()
    async def comrade(self, ctx, *, member: disnake.Member = None):
        if member is None:
            await self.overlay(ctx, "comrade")
        else:
            await self.overlay(ctx, "comrade", member)

    @commands.command()
    async def triggered(self, ctx, *, member: disnake.Member = None):
        await self.overlay(ctx, "triggered", member)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
