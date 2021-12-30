import disnake
from disnake.ext import commands
import random


class Fun(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["gaypercent","howgay"])
    async def gaymeter(self, ctx, member: disnake.Member=None) -> None:
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,101)}% gay")

    @commands.command(aliases=["Y_or_N","choose"])
    async def pick(self, ctx) -> None:
        await ctx.send(random.choice(["Yes","No"]))

    @commands.command(aliases=["cutepercent","howcute"])
    async def cutemeter(self, ctx,member: disnake.Member=None) -> None:
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,101)}% cute")

    @commands.command(aliases=["should_i"])
    async def options(self, ctx,*, options=None) -> None:
        if options is None:
            return await ctx.send("no options were given")

        await ctx.send(random.choice(options.split(",")))
    
    @commands.command(aliases=["love"])
    async def kiss(self, ctx, member: disnake.Member=None) -> None:
        if member is None:
            return await ctx.send(f"{ctx.author.mention} has kissed himself")
        embed1 = disnake.Embed(
            title=f"how cute,{ctx.author.mention} has kissed {member.name}").set_image(ur

        await ctx.send(embed=embed1)
    
    @commands.command(aliases=["smack","hit"])
    async def slap(self, ctx, member: disnake.Member=None) -> None:
        if member is None:
            return await ctx.send(f"{ctx.author.mention} has slapped himself")

        embed2 = disnake.Embed(
            title=f"{ctx.author.mention} has slapped {member.name}").set_image(url="https

        await ctx.send(embed=embed2)

    @commands.command(aliases=["simppercent"])
    async def simpmeter(self, ctx,member: disnake.Member=None) -> None:
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,101)}% a simp")

    @commands.command(aliases=["howbig"])
    async def ppmeter(self, ctx,member: disnake.Member=None) -> None:
        if member is None:
            member = ctx.author
        size = random.randint(1,13)
        if size <= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a small p
        elif size >= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a big pp"

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Fun(bot))
