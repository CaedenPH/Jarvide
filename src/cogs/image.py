import random
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
    async def emb(ctx, message, user = None, colorarg = None, **kwargs):
        user = user or ctx.author
        emb = Embed(
            description=message,
            color=colorarg or color,
        ).set_footer(text = f"{user}", icon_url = user.avatar.url)
        return await ctx.send(embed = emb)

    @staticmethod
    async def sendOverlay(ctx: Context, endpoint, params: dict, user: Member):
        user = user or ctx.author
        prms = ""
        for _i, v in enumerate(params):
            if len(params) > 0:
                prms += f"{'?' if _i == 0 else '&'}{v}={params[v].replace(' ', '+')}"
        url = f"https://some-random-api.ml{endpoint}{prms}"
        await ctx.send(embed = Embed(
            color = color
        ).set_author(
            name = user,
            icon_url = user.avatar.url
        ).set_image(
            url = url
        ))

    @command()
    async def gay(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        await sendOverlay(ctx, "/canvas/gay", {"avatar": user.avatar.with_format('png').url}, user)
    
    @command()
    async def wasted(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/wasted", {"avatar": user.avatar.with_format('png').url}, user)

    @command()
    async def jail(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/jail", {"avatar": user.avatar.with_format('png').url}, user)

    @command()
    async def passed(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/passed", {"avatar": user.avatar.with_format('png').url}, user)

    @command()
    async def triggered(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ct:, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/triggered", {"avatar": user.avatar.with_format('png').url}, user)

    @command()
    async def glass(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/glass", {"avatar": user.avatar.with_format('png').url}, user)

    @command()
    async def comrade(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/comrade", {"avatar": user.avatar.with_format('png').url}, user) 

    @command()
    async def grayscale(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/greyscale", {"avatar": user.avatar.with_format('png').url}, user) 

    @command()
    async def invert(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/invert", {"avatar": user.avatar.with_format('png').url}, user) 

    @command()
    async def brightness(self, ctx: Context, brightness: int, user: Member = None):
        user = user or ctx.author
        
        if brightness < 0 or brightness > 255:
            return await self.emb(ctx, f"Brightness should be between 0 - 255")
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/brightness", {"avatar": user.avatar.with_format('png').url, "brightness": brightness}, user) 
    
    @command(aliases = ['pixels', 'lowres', 'lowresolution'])
    async def pixelate(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/pixelate", {"avatar": user.avatar.with_format('png').url}, user) 

    @command()
    async def blur(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/blur", {"avatar": user.avatar.with_format('png').url}, user) 

    @command()
    async def simpcard(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/simpcard", {"avatar": user.avatar.with_format('png').url}, user) 
    
    @command()
    async def lolice(self, ctx: Context, *, user: Member = None):
        user = user or ctx.author
        
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/lolice", {"avatar": user.avatar.with_format('png').url}, user) 
    
    @command()
    async def youtube(self, ctx: Context, user: Union[Member, str] = None, *, message = None):
        
        if not user and not message:
            raise MissingRequiredArgument(Parameter('user', Parameter.POSITIONAL_ONLY, default = None))
        elif user and not message:
            raise MissingRequiredArgument(Parameter('message', Parameter.POSITIONAL_ONLY, default = None))
        if isinstance(user, str):
            message = ctx.message.content[len(ctx.prefix)+len(ctx.command.name)+1:]
            user = ctx.author
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/youtube-comment", {"avatar": user.avatar.with_format('png').url, "username": user.display_name, "comment": message}, user)
        
    @command()
    async def stupid(self, ctx: Context, user: Union[Member, str] = None, *, message = None):
        if not user and not message:
            raise MissingRequiredArgument(Parameter('user', Parameter.POSITIONAL_ONLY, default = None))
        elif user and not message:
            raise MissingRequiredArgument(Parameter('message', Parameter.POSITIONAL_ONLY, default = None))
        if isinstance(user, str):
            message = ctx.message.content[len(ctx.prefix)+len(ctx.command.name)+1:]
            user = ctx.author
        if user.avatar == None:
            return await self.emb(ctx, f"{user.mention} Doesnt have an avatar...")
        await sendOverlay(ctx, "/canvas/its-so-stupid", {"avatar": user.avatar.with_format('png').url, "dog": message}, user)

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
