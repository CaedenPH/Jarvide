import disnake, aiohttp, random

from disnake.ext import commands


class Misc(commands.Cog):
    """
    Misc cog for randomly assorted commands that don't fall into
    any specific category.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def overlay(ctx: commands.Context, endpoint, user = None):
                if user == None: user = ctx.author
                emb = disnake.Embed(
                    color = 0x90EE90
                ).set_image(url = f"https://some-random-api.ml/canvas/%s?avatar=%s" % (endpoint, user.avatar.with_format('png').url))
                await ctx.send(embed = emb)

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
                name="**Roundtrip**", value=f"```{round(self.bot.latency * 1000)} ms```"
            )
            .add_field(name="**Health**", value=f"```{health}```")
            .set_footer(text="Discord API issues could lead to high roundtrip times")
        )
        await ctx.send(content="🏓**Pong**", embed=embed)

    @commands.command(aliases = ['insult'])
    async def roast(self, ctx: commands.Context, *, user: disnake.Member = None):
      async with aiohttp.ClientSession() as cs:
          async with cs.get("https://evilinsult.com/generate_insult.php?lang=en&type=json") as res:
            resp = await res.json()
            insult = resp['insult']
            color = 0x90EE90
            embed = (
            disnake.Embed(color=color, description = insult)
        )
            await ctx.send(f"{user.mention}", embed=embed)
    
    @commands.command()
    async def meme(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://reddit.com/r/dankmemes.json?sort=hot") as resp:
                _json = await resp.json()
                color = 0x90EE90
                post = random.choice(_json['data']['children'])['data']
                embed = (
                    disnake.Embed(
                        color = color,
                        title = post['title'],
                        url = post['permalink']
                    ).set_image(url =post['url'])
                )
                await ctx.send(embed = embed)

    @commands.command()
    async def reddit(self, ctx: commands.Context, subreddit):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://reddit.com/r/{subreddit}.json?sort=hot") as resp:
                _json = await resp.json()
                post = random.choice(_json['data']['children'])['data']
                if 'url' in post:
                    embed = (
                        disnake.Embed(color= 0x90EE90, title = post['title'], url = post['permalink'])
                    ).set_image(url = post['url'])
                else:
                    embed = (
                        disnake.Embed(color= 0x90EE90, title = post['title'], url = post['permalink'], description = post['selftext'])
                    )

                await ctx.send(embed=embed)    

    @commands.command()
    async def gay(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "gay")
        else: await self.overlay(ctx, "gay", user)    
    
    @commands.command()
    async def wasted(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "wasted")
        else: await self.overlay(ctx, "wasted", user) 

    @commands.command()
    async def passed(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "passed")
        else: await self.overlay(ctx, "passed", user)     

    @commands.command()
    async def jail(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "jail")
        else: await self.overlay(ctx, "jail", user)    

    @commands.command()
    async def comrade(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "comrade")
        else: await self.overlay(ctx, "comrade", user)      
    
    @commands.command()
    async def triggered(self, ctx, *, user: disnake.Member = None):
        if user == None:
            await self.overlay(ctx, "triggered")
        else: await self.overlay(ctx, "triggered", user)    

def setup(bot: commands.Bot) -> None:
    """Setup misc cog"""
    bot.add_cog(Misc(bot))
