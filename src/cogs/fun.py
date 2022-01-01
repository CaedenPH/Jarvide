import disnake
from disnake.ext import commands
import random


class Fun(commands.Cog):
    """Fun cog for fun related commands"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["gaypercent", "howgay"])
    async def gaymeter(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% gay")

    @commands.command(aliases=["Y_or_N", "choose"])
    async def pick(self, ctx) -> None:
        await ctx.send(random.choice(["Yes", "No"]))

    @commands.command(aliases=["cutepercent", "howcute"])
    async def cutemeter(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% cute")

    @commands.command(aliases=["should_i"])
    async def options(self, ctx, *, options=None) -> None:
        if options is None:
            return await ctx.send("no options were given")

        await ctx.send(random.choice(options.split(",")))

    @commands.command(aliases=["love"])
    async def kiss(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            return await ctx.send(f"{ctx.author.mention} has kissed himself")
        embed1 = disnake.Embed(
            title=f"how cute, {ctx.author.mention} has kissed {member.name}").set_image(
            url="https://media.tenor.co/videos/fc567d93fe70d2e0567325df0410959b/mp4")

        await ctx.send(embed=embed1)

    @commands.command(aliases=["smack", "hit"])
    async def slap(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            return await ctx.send(f"{ctx.author.mention} has slapped himself")

        embed2 = disnake.Embed(
            title=f"{ctx.author.mention} has slapped {member.name}").set_image(
            url="https://media.tenor.co/videos/318d19d23b24c54ab51cacf5ef4bfccf/mp4")

        await ctx.send(embed=embed2)

    @commands.command(aliases=["simppercent"])
    async def simpmeter(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% a simp")

    @commands.command(aliases=["howbig"])
    async def ppmeter(self, ctx, member: disnake.Member = None) -> None:
        if not member:
            member = ctx.author
        size = random.randint(1, 12)
        if size <= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a small pp")
        elif size >= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a big pp")


def setup(bot: commands.Bot) -> None:
    """Setup fun cog"""
    bot.add_cog(Fun(bot))
