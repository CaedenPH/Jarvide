import disnake
from disnake.ext import commands
import random

class Casino(disnake.ui.View):
    """subclass for buttons in jackpot command"""

    def __init__(self, author: disnake.Member) -> None:
        self.author = author
        super().__init__(timeout=60.0)
        self.children[1].disabled = True
        
    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
            self.stop()
    

    @disnake.ui.button(label="Play", style=disnake.ButtonStyle.green, emoji="▶️")
    async def play(self, button: disnake.ui.button, interaction: disnake.MessageInteraction) -> None:
        self.children[0].disabled = True
        intsthink = disnake.Embed(
            title="Casino Machine $",
            description="```...```").set_footer(text="Get Three numbers in a row for a PRIZE")
        
        await interaction.response.edit_message(embed=intsthink, view=self)
        
        Afirstint = random.randint(1, 9)
        Asecondint = random.randint(1, 9)
        Athirdint = random.randint(1, 9)

        ints = disnake.Embed(
            title="Casino Machine $",
            description=f"```{Afirstint}{Asecondint}{Athirdint}```").set_footer(text="Get Three numbers in a row for a PRIZE")

        self.children[1].disabled = False

        await interaction.edit_original_message(embed=ints, view=self)

        if Afirstint == Asecondint ==  Athirdint:
            Awinningembed = disnake.Embed(
                title="WINNER",
                description=f"{interaction.author.mention} has won {random.randint(1,1000)}$")
            self.stop()
            return await interaction.send(embed=Awinningembed, view=None)
    
    @disnake.ui.button(label="Retry", style=disnake.ButtonStyle.green, emoji="🔄")
    async def retry(self, button: disnake.ui.button, interaction: disnake.MessageInteraction) -> None:

        intsthink1 = disnake.Embed(
            title="Casino Machine $",
            description="```...```").set_footer(text="Get Three numbers in a row for a PRIZE")

        self.children[1].disabled = True

        await interaction.response.edit_message(embed=intsthink1, view=self)

        Bfirstint = random.randint(1, 9)
        Bsecondint = random.randint(1, 9)
        Bthirdint = random.randint(1, 9)

        ints1 = disnake.Embed(
            title="Casino Machine $",
            description=f"```{Bfirstint}{Bsecondint}{Bthirdint}```").set_footer(text="Get Three numbers in a row for a PRIZE")

        self.children[1].disabled = False

        await interaction.edit_original_message(embed=ints1, view=self)

        if Bfirstint == Bsecondint ==  Bthirdint:
            Bwinningembed = disnake.Embed(
                title="WINNER",
                description=f"{interaction.author.mention} has won {random.randint(1,1000)}$")
            self.stop()
            return await interaction.send(embed=Bwinningembed, view=None)
    
    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.red ,emoji="⏹️")
    async def exit(self, button: disnake.ui.button, interaction: disnake.MessageInteraction) -> None:
        await interaction.edit_original_message(view=None)
        self.stop()


class Fun(commands.Cog):
    """Fun cog for fun related commands"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command(aliases=["gaypercent", "howgay"])
    async def gaymeter(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,100)}% gay")


    @commands.command(aliases=["Y_or_N", "choose"])
    async def pick(self, ctx) -> None:
        await ctx.send(random.choice(["Yes", "No"]))


    @commands.command(aliases=["cutepercent", "howcute"])
    async def cutemeter(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,100)}% cute")


    @commands.command(aliases=["should_i"])
    async def options(self, ctx, *, options=None) -> None:
        if options is None:
            return await ctx.send("no options were given")

        await ctx.send(random.choice(options.split(",")))
    

    @commands.command(aliases=["love"])
    async def kiss(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            return await ctx.send(f"{ctx.author.mention} has kissed himself")
        embed1 = disnake.Embed(
            title=f"how cute, {ctx.author.mention} has kissed {member.name}").set_image(url="https://media.tenor.co/videos/fc567d93fe70d2e0567325df0410959b/mp4")

        await ctx.send(embed=embed1)
    

    @commands.command(aliases=["smack", "hit"])
    async def slap(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            return await ctx.send(f"{ctx.author.mention} has slapped himself")

        embed2 = disnake.Embed(
            title=f"{ctx.author.mention} has slapped {member.name}").set_image(url="https://media.tenor.co/videos/318d19d23b24c54ab51cacf5ef4bfccf/mp4")

        await ctx.send(embed=embed2)


    @commands.command(aliases=["simppercent"])
    async def simpmeter(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1,100)}% a simp")


    @commands.command(aliases=["howbig"])
    async def ppmeter(self, ctx, member: disnake.Member=None) -> None:
        if not member:
            member = ctx.author
        size = random.randint(1,12)
        if size <= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a small pp")
        elif size >= 6:
            await ctx.send(f"{member.mention} is packing {size}inches, wow such a big pp")

    @commands.command(aliases=["casino"])
    async def jackpot(self, ctx) -> None:
        embed20 = disnake.Embed(
            title="Casino Machine $",
            description="```000```").set_footer(text="Get Three numbers in a row for a PRIZE")
    
        await ctx.send(embed=embed20, view=Casino())

def setup(bot: commands.Bot) -> None:
    """Setup fun cog"""
    bot.add_cog(Fun(bot))
