import disnake
import random
import praw
from redditSettings import reddit
from disnake.ui import View, button, Button

from disnake import (
    Embed, 
    Member,
    MessageInteraction,
    ButtonStyle
)
from disnake.ext.commands import (
    Cog,
    CooldownMapping, 
    BucketType,
    Context,
    command
)
from ..bot import Jarvide

class Image(
    Cog,
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, 3.5, BucketType.user)},
):
    """
    Imagine yourself in prison...this image manipulation cog makes dreams reality!
    """

    def __init__(self, bot: Jarvide) -> None:
        self.bot = bot  

        self.emoji = "🖼️"
        self.short_help_doc = "Awesome image manipulation"


    @staticmethod
    async def overlay(ctx: Context, endpoint: str, member: Member = None) -> None:
        """Shortcut method for sending image"""

        member = member or ctx.author
        await ctx.send(
            embed=Embed(color=0x90EE90)
            .set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            .set_image(
                url=f"https://some-random-api.ml/canvas/{endpoint}?avatar={member.avatar.with_format('png').url}"
            )
        )

    @command()
    async def gay(self, ctx: Context, member: Member = None):
        """Gay'ify a profile picture!"""

        await self.overlay(ctx, "gay", member)

    @command()
    async def wasted(self, ctx: Context, member: Member = None):
        """Waste'tify a profile picture!"""

        await self.overlay(ctx, "wasted", member)

    @command()
    async def jail(self, ctx: Context, member: Member = None):
        """Jail'ify a profile picture!"""

        await self.overlay(ctx, "jail", member)

    @command()
    async def triggered(self, ctx: Context, member: Member = None):
        """Trigger'ify a profile picture!"""

        await self.overlay(ctx, "triggered", member)

class Meme(View):
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
    @button(label="Next", style=ButtonStyle.green, emoji="⏭️")
    async def meme(self, button: Button, interaction: MessageInteraction) -> None:
        subreddit = reddit.subreddit("memes")
        all_posts = []
        hot = subreddit.hot(limit=50)
        for post in hot:
            all_posts.append(post)
        random_post = random.choice(all_posts)
        name = random_post.title
        url = random_post.url
        embed = Embed(
            title = name,
            color = 0x8b008b
            ).set_image(
                url = url
            ).set_footer(
                text = f"Requested by {interaction.author.name} *Note: there are only 50 memes within one meme command, for more do `jarvide meme` again*",
                icon_url=interaction.author.display_avatar.url
            )
        await interaction.response.defer()
        await interaction.edit_original_message(embed=embed, view=self)

    @button(label="Exit", style=ButtonStyle.red, emoji="⏹️")
    async def exit(self, button: Button, interaction: MessageInteraction) -> None:
        await interaction.response.defer()
        await interaction.edit_original_message(view=None)
        self.stop()

@command(aliases=["m", "memes"])
async def meme(self, ctx: Context):
    embed = Embed(title = "<:reddit:933846462087987292> Memes <:reddit:933846462087987292>",
    description = "Get your daily dose of reddit memes!",
    color = 0x8b008b).set_footer(
        text = f"Requested by {ctx.author.name} *Note: there are only 50 memes within one meme command, for more do `jarvide meme` again*",
        icon_url = ctx.author.display_avatar.url
    )


def setup(bot: Jarvide) -> None:
    bot.add_cog(Image(bot))