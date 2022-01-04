import os
import string
import copy
from disnake import Message

from disnake.ext.commands import (
    Bot,
    BotMissingPermissions,
    MissingPermissions,
    MissingRole,
    CommandNotFound,
    DisabledCommand,
    NotOwner,
    ChannelNotFound,
    MemberNotFound,
    UserNotFound,
    TooManyArguments,
    CommandOnCooldown,
    MissingRequiredArgument,
    Context
)
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

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
]


class Jarvide(Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,  # type: ignore
        )
        self.engine = AIOEngine(AsyncIOMotorClient(MONGO_URI))
        self.send_guild = None

    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.startswith("_") and filename.endswith("py"):
                self.load_extension(f"src.cogs.{filename[:-3]}")

        self.load_extension("src.cogs.ide.ide")
        self.load_extension("jishaku")

    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def on_message(self, original_message: Message) -> None:
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
        message_content = "".join(
            [
                char
                for char in original_message.content
                if char not in string.punctuation
            ]
        )

        message_content = " ".join(
            word for word in message_content.split() if word != "jarvide"
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
        userAuthorized = await cmd.can_run(ctx)

        if userAuthorized:
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
        print("Set up")

    async def on_command_error(self, ctx: Context, error: Exception):
        if isinstance(error, MissingRequiredArgument):
            return await ctx.send(f'```py\n{ctx.command.name} {ctx.command.signature}\n```\nNot enough arguments passed.')

        elif isinstance(error, CommandNotFound):
            return

        elif isinstance(error, DisabledCommand):
            return await ctx.send('This command is disabled.')

        elif isinstance(error, TooManyArguments):
            return await ctx.send('Too many arguments passed.')

        elif isinstance(error, CommandOnCooldown):
            return await ctx.send('Command is on cooldown. Try again later.')

        elif isinstance(error, NotOwner):
            return await ctx.send('Only my owner can use this command.')

        elif isinstance(error, MemberNotFound):
            return await ctx.send('No such member found.')

        elif isinstance(error, UserNotFound):
            return await ctx.send('No such user found.')   

        elif isinstance(error, ChannelNotFound):
            return await ctx.send('No such channel found.')

        elif isinstance(error, MissingPermissions):
            return await ctx.send('You cannot invoke this command because you do not have enough permissions.')

        elif isinstance(error, BotMissingPermissions):
            return await ctx.send('I cannot execute this command because I am missing certain permissions.')

        elif isinstance(error, MissingRole):
            return await ctx.send('You are missing a certain role to perform this command.')