import asyncio

from disnake import MessageInteraction, Embed, Member, ButtonStyle
from disnake.ext.commands import Cog, Bot, command, guild_only, Context

import random
from disnake.ui import View, button, Button


class Casino(View):
    def __init__(self, author: Member) -> None:
        self.author = author
        super().__init__(timeout=60.0)
        self.retry.disabled = True

    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
            self.stop()

    @button(
        label="Play",
        style=ButtonStyle.green,
        emoji="▶️",
    )
    async def play(self, button: Button, interaction: MessageInteraction) -> None:
        self.exit.disabled = True
        self.play.disabled = True
        intsthink = Embed(title="Casino Machine $", description="```...```").set_footer(
            text="Get Three numbers in a row for a PRIZE"
        )

        await interaction.response.edit_message(embed=intsthink, view=self)

        r_ints = (random.randint(1, 9), random.randint(1, 9), random.randint(1, 9))
        result, ints = [], None

        for i in r_ints:
            result.append(str(i))
            ints = Embed(
                title="Casino Machine $", description=f"```{''.join(result)}```"
            ).set_footer(text="Get Three numbers in a row for a PRIZE")
            await interaction.edit_original_message(embed=ints, view=self)
            await asyncio.sleep(1)

        self.retry.disabled = False
        self.exit.disabled = False
        await interaction.edit_original_message(embed=ints, view=self)

        if len(set(r_ints)) == 1:
            awinningembed = Embed(
                title="WINNER",
                description=f"{interaction.author.mention} has won {random.randint(1, 1000)}$",
            )
            self.stop()
            return await interaction.send(embed=awinningembed)

    @button(label="Retry", style=ButtonStyle.green, emoji="🔄")
    async def retry(self, button: Button, interaction: MessageInteraction) -> None:
        intsthink1 = Embed(
            title="Casino Machine $", description="```...```"
        ).set_footer(text="Get Three numbers in a row for a PRIZE")
        self.exit.disabled = True
        await interaction.response.edit_message(embed=intsthink1, view=self)

        r_ints = (random.randint(1, 9), random.randint(1, 9), random.randint(1, 9))

        result, ints = [], None
        for i in r_ints:
            result.append(str(i))
            ints = Embed(
                title="Casino Machine $", description=f"```{''.join(result)}```"
            ).set_footer(text="Get Three numbers in a row for a PRIZE")
            await interaction.edit_original_message(embed=ints, view=self)
            await asyncio.sleep(1)

        self.retry.disabled = False
        self.exit.disabled = False
        await interaction.edit_original_message(embed=ints, view=self)

        if len(set(r_ints)) == 1:
            bwinningembed = Embed(
                title="WINNER",
                description=f"{interaction.author.mention} has won {random.randint(1, 1000)}$",
            )
            self.stop()
            return await interaction.send(embed=bwinningembed)

    @button(label="Exit", style=ButtonStyle.red, emoji="⏹️")
    async def exit(self, button: Button, interaction: MessageInteraction) -> None:
        await interaction.response.defer()
        await interaction.edit_original_message(view=None)
        self.stop()


class Fun(Cog):
    """Fun cog for fun related commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.emoji = "🍿"
        self.short_help_doc = "Fun commands to play around with!"

    @command()
    async def howgay(self, ctx, member: Member = None) -> None:
        """Shows how gay you are."""
        if not member:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% gay")

    @command()
    async def howcute(self, ctx: Context, member: Member = None):
        """Shows how cute you are."""
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% cute!")

    @command()
    async def choose(self, ctx: Context, *arguments):
        """Chooses between multiple choices."""

        await ctx.send(random.choice(arguments))

    @command()
    @guild_only()
    async def kiss(self, ctx: Context, member: Member = None):
        """Kiss a member."""

        if not member:
            return await ctx.send(f"You didn't mention a member.")

        embed1 = Embed(
            title=f"how cute, {ctx.author.mention} has kissed {member.name}"
        ).set_image(
            url="https://media.tenor.co/videos/fc567d93fe70d2e0567325df0410959b/mp4"
        )

        await ctx.send(embed=embed1)

    @command()
    @guild_only()
    async def slap(self, ctx: Context, member: Member = None) -> None:
        """Slap a member."""
        if member is None:
            return await ctx.send("You didn't mention a member.")

        embed2 = Embed(
            title=f"{ctx.author.mention} has slapped {member.name}"
        ).set_image(
            url="https://media.tenor.co/videos/318d19d23b24c54ab51cacf5ef4bfccf/mp4"
        )

        await ctx.send(embed=embed2)

    @command()
    async def simpmeter(self, ctx: Context, member: Member = None) -> None:
        """Shows how much of a simp you are."""
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% a simp!")

    @command()
    async def ppmeter(self, ctx: Context, member: Member = None) -> None:
        """Shows your how long is your pp."""
        if member is None:
            member = ctx.author

        inches = random.randint(1, 12)
        size = "small" if inches <= 6 else "big"

        await ctx.send(
            f"{member.mention} is packing {inches} inches, wow such a {size} pp!"
        )

    @command()
    async def casino(self, ctx: Context) -> None:
        """Play the casino!"""
        embed20 = Embed(title="Casino Machine $", description="```000```").set_footer(
            text="Get Three numbers in a row for a PRIZE"
        )

        await ctx.send(embed=embed20, view=Casino(ctx.author))


def setup(bot: Bot) -> None:
    bot.add_cog(Fun(bot))
