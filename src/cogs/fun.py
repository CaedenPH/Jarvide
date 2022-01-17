import asyncio
from time import time
import disnake
import random
import aiohttp

from disnake import MessageInteraction, Embed, Member, ButtonStyle
from disnake.ui import View, button, Button
from disnake.ext.commands import (
    Cog, 
    command, 
    guild_only, 
    Context,
    CooldownMapping,
    BucketType
)
from typing import Optional

from ..bot import Jarvide

class Casino(View):
    def __init__(self, author: Member) -> None:
        self.author = author
        super().__init__(timeout=60.0)
        self.retry.disabled = True

    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
            self.stop()

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if interaction.author != self.author:
            return False
        return True

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
            await asyncio.sleep(0.2)

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
            await asyncio.sleep(0.2)

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

class RussianRoulette(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)

        self.ctx = ctx

    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
            self.stop()

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="Play", style=ButtonStyle.green, emoji="▶️")
    async def play(self, button: Button, interaction: MessageInteraction) -> None:
        random_choice = random.choice(['🌹 / **You lived**','<:gun:931861130488467456> / **You died**'])
        embed_colour = {"🌹 / **You lived**":0x32CD32, "<:gun:931861130488467456> / **You died**":0x8B0000}

        footer_text = random.choice(
            ["loves to play this game", 
            "must like excitement", 
            "is definitely a risk taker",
            "definitely hates life", 
            "plays this game 24/7", 
            "has issues",
            "probably needs some help"
            ]
        )

        embed = Embed(
            description=random_choice,
            colour=embed_colour[random_choice]
        ).set_footer(
            text=f"{interaction.author.name} {footer_text}", 
            icon_url=(interaction.author.display_avatar.url)
        )

        await interaction.response.defer()
        await interaction.edit_original_message(embed=embed, view=self)


    @button(label="Exit", style=ButtonStyle.red, emoji="⏹️")
    async def exit(self, button: Button, interaction: MessageInteraction) -> None:
        await interaction.response.defer()
        await interaction.edit_original_message(view=None)
        self.stop()


class Fun(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """Fun cog for fun related commands."""

    def __init__(self, bot: Jarvide) -> None:
        self.bot = bot

        self.emoji = "🍿"
        self.short_help_doc = "Fun commands to play around with!"

    @command(aliases=["gaymeter", "gaypercent"])
    async def howgay(self, ctx, member: Member = None) -> None:
        """Shows how gay you are."""

        member = member or ctx.author
        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% gay")

    @command(aliases=["cutemeter", "cutepercent"])
    async def howcute(self, ctx: Context, member: Member = None):
        """Shows how cute you are."""

        member = member or ctx.author
        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% cute!")

    @command(aliases=["howsimp"])
    async def simpmeter(self, ctx: Context, member: Member = None) -> None:
        """Shows how much of a simp you are."""

        member = member or ctx.author
        await ctx.send(f"{member.mention} is {random.randint(1, 100)}% a simp!")

    @command(aliases=["howlongpp", "pplength"])
    async def ppmeter(self, ctx: Context, member: Member = None) -> None:
        """Shows your how long is your pp."""

        member = member or ctx.author
        inches = random.randint(1, 12)
        size = "small" if inches <= 6 else "big"

        await ctx.send(
            f"{member.mention} is packing {inches} inches, wow such a {size} pp!"
        )

    @command(aliases=["pick", "random"])
    async def choose(self, ctx: Context, *arguments):
        """Chooses between multiple choices."""

        if not arguments:
            return await ctx.send("Uh oh! You didn't specify anything for me to choose from...")
        await ctx.send(random.choice(arguments))

    @command()
    async def casino(self, ctx: Context) -> None:
        """Play the casino!"""
        
        embed = Embed(title="Casino Machine $", description="```000```").set_footer(
            text="Get Three numbers in a row for a PRIZE"
        )
        await ctx.send(embed=embed, view=Casino(ctx.author))

    @command(aliases=["8ball", "8_ball", "eightball"])
    async def eight_ball(self, ctx: Context, *, message: str):
        """Responds to a user's question with a random answer."""

        random_response = random.choice([
            "yes", "no", "maybe", "that is true", "absolutely false", "stop the cap",
            "there is an argument against that", "I think that is true", "probably",
            "really?", "you shouldn't have to be asking me this", "100% true",
            "100% false", "negative", "facts", "not the best", "you could do better"
        ])
        embed = Embed(title="<:8_ball:932328134861275196> 8Ball <:8_ball:932328134861275196>",
                       description=f"Question:`{message}`\nAnswer:`{random_response}`", colour=0x301934).set_footer(
             text=f"asked by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        return await ctx.reply(embed=embed)

    @command(aliases=["rr", "gun_game", "russianroulette", "gungame"])
    async def russian_roulette(self, ctx: Context):
        """Play a scary game of russian roulette...will you live or die?"""

        embed = Embed(title="Russian Roulette").set_footer(
            text="Dont die!"
        )
        await ctx.send(embed=embed, view=RussianRoulette(ctx))

    @command(aliases=["insult"])
    async def roast(self, ctx: Context, member: Member):
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



def setup(bot: Jarvide) -> None:
    bot.add_cog(Fun(bot))
