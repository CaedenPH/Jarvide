import os
import string
import copy
import typing
import traceback
import random

from disnake import Message
from disnake.ext.commands import (
    Bot,
    BotMissingPermissions,
    MissingPermissions,
    MissingRole,
    DisabledCommand,
    NotOwner,
    ChannelNotFound,
    MemberNotFound,
    UserNotFound,
    TooManyArguments,
    CommandOnCooldown,
    MissingRequiredArgument,
    Context,
)
from disnake import Intents, Embed, Color
from disnake.ext.commands.errors import CommandNotFound
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from src.utils.utils import main_embed
from .HIDDEN import TOKEN, MONGO_URI

REMOVE_WORDS = [
    "what",
    "pls",
    "tell",
    "me",
    "the",
    "tf",
    "give",
    "your",
    "you",
    "is",
    "can",
    "fuck",
    "shit",
    "me",
    "this",
    "mf",
]


class Jarvide(Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,  # type: ignore
            intents=Intents.all(),
        )
        self.engine = AIOEngine(AsyncIOMotorClient(MONGO_URI))
        self.send_guild = None
        self.error_channel = None
        self.server_message = None
        self.bugs =  range(10000, 100000)

    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.startswith("_") and filename.endswith("py"):
                self.load_extension(f"src.cogs.{filename[:-3]}")

        self.load_extension("src.cogs.ide.ide")
        self.load_extension("jishaku")

    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def on_message(self, original_message: Message) -> typing.Optional[Message]:
        if original_message.content in [f"<@!{self.user.id}>", f"<@{self.user.id}>"]:
            return await original_message.channel.send(embed=main_embed(self))
        if (
            original_message.author.bot
            or "jarvide" not in original_message.content.lower()
        ):
            return
        original_message.content = " ".join(
            [
                word
                for word in original_message.content.lower().split()
                if not any(
                    word.startswith(censored_word) for censored_word in REMOVE_WORDS
                )
            ]
        )
        original_message.content = "".join(
            [
                char
                for char in original_message.content
                if (char in string.ascii_letters or char.isspace())

            ]
        )
        message_content = " ".join(
            word for word in original_message.content.split() if word != "jarvide"
        )

        list_of_commands = {c: [c.name, *c.aliases] for c in self.commands}
        commands_in_message = list(
            filter(
                lambda c: any([x in message_content.split() for x in c[1]]),
                list_of_commands.items(),
            )
        )
        if len(commands_in_message) <= 0:
            return

        if "help" in [k[0].name for k in commands_in_message]:
            if commands_in_message[0][0].name != "help":
                commands_in_message = commands_in_message[::-1]

        cmd = commands_in_message[0][0]
        ctx = await super().get_context(original_message)
        user_authorized = await cmd.can_run(ctx)
        if user_authorized:
            args = original_message.content.partition(
                [
                    i
                    for i in list_of_commands[cmd]
                    if i in original_message.content.lower()
                ][0]
            )[2]

            new_message = copy.copy(original_message)
            new_message.content = f"jarvide {cmd.name}{args}"
            await super().process_commands(new_message)

    async def on_ready(self) -> None:
        self.send_guild = self.get_guild(926811692019626064)
        self.report_channel = self.get_channel(928402833475264572)
        self.error_channel = self.get_channel(927596019468873748)
        channel = self.get_channel(927523239259942972)
        self.server_message = await channel.fetch_message(927971357738811463)
        print("Set up")

    async def on_guild_join(self, guild) -> None:
        await self.server_message.edit(
            content=f"I am now in `{len(self.guilds)}` servers and can see `{len(self.users)}` users"
        )

        embed = main_embed(self)
        names = [
            "general",
            "genchat",
            "generalchat",
            "general-chat",
            "general-talk",
            "gen",
            "talk",
            "general-1",
            "🗣general-chat",
            "🗣",
            "🗣general",
        ]
        for k in guild.text_channels:
            if k.name in names:
                return await k.send(embed=embed)
        try:
            await guild.system_channel.send(embed=embed)
        except:
            pass  # TODO: see what errors it raises

    @staticmethod
    def underline(text, at, for_):
        underline = (" " * at) + ("^" * for_)
        return text + "\n" + underline

    async def on_command_error(self, ctx: Context, error: Exception):
        if isinstance(error, CommandNotFound):
            return

        elif isinstance(error, MissingRequiredArgument):
            desc = f"{ctx.prefix} {ctx.command.name} {ctx.command.signature}"
            inside = self.underline(
                desc, desc.index(f"<{error.param.name}>"), len(f"<{error.param.name}>")
            )
            desc = f"You missed an argument: \n```\n{inside}\n```"
            return await ctx.send(desc)

        elif isinstance(error, DisabledCommand):
            return await ctx.send("This command is disabled.")

        elif isinstance(error, TooManyArguments):
            return await ctx.send(
                f"Too many arguments passed.\n```yaml\nusage: {ctx.prefix}"
                f"{ctx.command.aliases.append(ctx.command.name)} {ctx.command.signature} "
            )

        elif isinstance(error, CommandOnCooldown):
            title = ["Slow down!", "You're going a little too fast bud...", "Hold your horses!",
             "Noooooo!", "Woah now, slow it down...", "Take a breather...", "NEGATORY."]
            cooldown_embed = Embed(
                title=random.choice(title),
                description=f"This command is on a cooldown! try again in `{round(error.retry_after, 2)}` seconds.",
                color=Color.red()
            )
            await ctx.send(embed=cooldown_embed)

        elif isinstance(error, NotOwner):
            return await ctx.send("Only my owner can use this command.")

        elif isinstance(error, MemberNotFound):
            return await ctx.send("No such member found.")

        elif isinstance(error, UserNotFound):
            return await ctx.send("No such user found.")

        elif isinstance(error, ChannelNotFound):
            return await ctx.send("No such channel found.")

        elif isinstance(error, MissingPermissions):
            return await ctx.send(
                f'You need the {"".join(error.missing_permissions)} permissions to be able to do this.'
            )

        elif isinstance(error, BotMissingPermissions):
            return await ctx.send(
                f'I need the {"".join(error.missing_permissions)} permissions to be able to do this.'
            )

        elif isinstance(error, MissingRole):
            return await ctx.send(
                "You are missing a certain role to perform this command."
            )
        else:
            await ctx.send(
                "An unexpected error occurred! Reporting this to my developer..."
            )
            await self.error_channel.send(
                # type: ignore
                f"```yaml\n{''.join(traceback.format_exception(error, error, error.__traceback__))}\n```"
            )
            raise error
