import aiohttp
import asyncio
import base64
import disnake
import math
import re
import simpleeval

from disnake.ext import commands
from typing import Optional

from src.utils.utils import File, get_info, EmbedFactory
from src.cogs.ide.dialogs import FileView

functions = {
    "sqrt": lambda x: math.sqrt(x),
    "sin": lambda x: math.sin(x),
    "cos": lambda x: math.cos(x),
    "tan": lambda x: math.tan(x),
    "ceil": lambda x: math.ceil(x),
    "floor": lambda x: math.floor(x),
    "sinh": lambda x: math.sinh(x),
    "cosh": lambda x: math.cosh(x),
    "tanh": lambda x: math.tanh(x),
    "abs": lambda x: math.fabs(x),
    "log": lambda x: math.log(x)
}


class OpenIDEButton(disnake.ui.View):
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx: commands.Context, file: File, bot_message):
        self.ctx = ctx
        self.file = file
        self.clicked = False
        self.bot_message = bot_message
        super().__init__(timeout=15)

    async def on_timeout(self) -> None:
        if not self.clicked:
            await self.bot_message.delete()

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Open in IDE", row=1)
    async def callback(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.clicked = True
        await interaction.response.defer()

        description = await get_info(self.file)
        embed = EmbedFactory.ide_embed(self.ctx, description)

        view = FileView(self.ctx, self.file, self.bot_message)
        view.bot_message = await self.bot_message.edit(
            content=None, embed=embed, view=view
        )
        if self.ctx.channel not in self.ctx.bot.active_commands:
            self.ctx.bot.active_commands[self.ctx.channel] = {}
        self.ctx.bot.active_commands[self.ctx.channel][
            self.ctx.author
        ] = view.bot_message.id


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.ignore = True
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def github_url(self, message: disnake.Message) -> None:
        if (
            message.channel in self.bot.active_commands
            and message.author in self.bot.active_commands[message.channel]
        ):
            return

        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        regex = re.compile(
            r"https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)/blob/(?P<branch>\w+)"
            r"/(?P<path>[^#>]+)#?L?(?P<linestart>\d+)?-?L?(?P<lineend>\d+)?"
        )
        try:
            repo, branch, path, start, end = re.findall(regex, message.content)[0]
        except IndexError:
            return
        await message.edit(suppress=True)
        async with aiohttp.ClientSession() as session:
            a = await session.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            json = await a.json()
            if "content" not in json:
                b = await session.get(
                    f"https://raw.githubusercontent.com/{repo}/{branch}/{path}",
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                content = (await b.text()).replace("`", "`​")
                if content == "404: Not Found":
                    return
            else:
                content = base64.b64decode(json["content"]).decode("utf-8")
        if start and end:
            content = "\n".join(content.splitlines()[int(start) - 1: int(end)])
        elif start and not end:
            content = content.splitlines()[int(start) - 1]
        file_ = File(content=content, filename=path.split("/")[-1], bot=self.bot)

        _message = await ctx.send("Fetching github link...")
        await asyncio.sleep(2)
        await _message.edit(
            content="Working github link found!\nTo disable this type `jarvide removeconfig github`",
            view=OpenIDEButton(ctx, file_, _message),
        )

    @commands.Cog.listener("on_message")
    async def file_detect(self, message: disnake.Message) -> Optional[disnake.Message]:
        if (
            message.channel in self.bot.active_commands
            and message.author in self.bot.active_commands[message.channel]
        ):
            return

        if message.author.bot or not message.attachments:
            return

        ctx = await self.bot.get_context(message)
        real_file = message.attachments[0]
        try:
            file_ = File(
                content=await real_file.read(),
                filename=real_file.filename,
                bot=self.bot,
            )

        except UnicodeDecodeError:
            return

        _message = await ctx.send("Resolving file integrity...")
        await asyncio.sleep(2)
        await _message.edit(
            content="Readable file found\nTo disable this type `jarvide removeconfig file`!",
            view=OpenIDEButton(ctx, file_, _message),
        )

    @commands.Cog.listener("on_message")
    async def codeblock_detect(
        self, message: disnake.Message
    ) -> Optional[disnake.Message]:
        if (
            message.channel in self.bot.active_commands
            and message.author in self.bot.active_commands[message.channel]
        ):
            return

        if message.author.bot:
            return

        if not (message.content.startswith("```") and message.content.endswith("```")):
            return

        ctx = await self.bot.get_context(message)
        clean_message = disnake.utils.remove_markdown(message.content).splitlines()
        extension, content = clean_message[0], "".join(clean_message[1:])
        try:
            file_ = File(
                content=content,
                filename=f"unamed.{extension}",
                bot=self.bot,
            )
        except UnicodeDecodeError:
            return

        _message = await ctx.send("Resolving code block integrity...")
        await asyncio.sleep(2)
        await _message.edit(
            content="Valid codeblock found!\nTo disable this type `jarvide removeconfig codeblock`",
            view=OpenIDEButton(ctx, file_, _message),
        )

    @commands.Cog.listener("on_message")
    async def calc_detect(self, message: disnake.Message) -> Optional[disnake.Message]:
        operators = r"\+\-\/\*\(\)\^\÷\."
        # if not 'jarivde' in message.content and message.guild in remove_configs:
        #     return
        # TODO: config shit here
        if re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message.content.lower()):
            return
        if not any(m in message.content for m in operators):
            return
        if message.author.bot:
            return

        for key, value in {
            "^": "**",
            "÷": "/",
            " ": "",
        }.items():
            message.content = message.content.replace(key, value)
        try:
            # Syntax:
            # 1. See if at least one function or one statement (E.g 1+2) exists, else return
            # 2. Parentheses multiplication is a valid syntax in math, so substitute `<digit*>"("` with `<digit*>"*("`
            # 3. It is possible that the first character in the equation is either "-", "+", or "(", so include it
            # 4. Functions is implemented here, so with functions the syntax would be `[<func>"("<expr*>")"]`
            # 5. Multiple parent/operators also possible, so we do `<digit*>[operators*][digit*]`, operators as wildcard
            # 6. Get the first match of all possible equations
            regex = re.compile(rf"(\d+|{'|'.join(list(functions.keys()))})[{operators}]+\d+")
            match = re.search(regex, message.content)
            if not match:
                return

            def parse(_match):
                return _match.group().replace("(", "*(")

            message.content = re.sub(re.compile(r"\d\("), parse, message.content)  # type: ignore
            funcs = "|".join(list(functions.keys()))
            regex = re.compile(
                rf"((([{operators}]+)?({funcs})?([{operators}]+)?(\d+[{operators}]+)*(\d+)([{operators}]+)?)+)"
            )
            match = re.findall(regex, message.content)
            content = match[0][0]
            if not any(m in content for m in operators) or not content:
                return
        except AttributeError:
            return
        embed = (
            disnake.Embed(color=disnake.Color.green())
            .set_footer(
                text="To disable this type jarvide removeconfig calc",
                icon_url=message.author.avatar.url,
            )
            .add_field(
                name="I detected an expression!",
                value=f'```yaml\n"{content}"\n```',
                inline=False,
            )
        )

        try:
            result = simpleeval.simple_eval(content, functions=functions)
            embed.add_field(name="Result: ", value=f"```\n{result}\n```")

        except ZeroDivisionError:
            embed.add_field(
                name="Wow...you make me question my existance",
                value="```yaml\nImagine you have zero cookies and you split them amongst 0 friends, how many cookies does each friend get? See, it doesn't make sense and Cookie Monster is sad that there are no cookies, and you are sad that you have no friends.```",
            )
        except simpleeval.FeatureNotAvailable:
            return await message.channel.send(
                "That syntax is not available currently, sorry!"
            )
        except SyntaxError:
            return
        except simpleeval.NumberTooHigh:
            return await message.channel.send("Oops, that number is too high to count.")
        try:
            await message.channel.send(embed=embed)
        except disnake.HTTPException:
            return


def setup(bot):
    bot.add_cog(Listeners(bot))
