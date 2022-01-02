import disnake
import os
import string
import aiosqlite
import copy

from typing import Optional

from .HIDDEN import TOKEN
from disnake.ext import commands


class Jarvide(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,  # type: ignore
            intents=disnake.Intents.all(),
        )
        self.db = None
        self.send_guild = None
        self.loop.create_task(self.connect_database())

    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.endswith(".py") and not filename.startswith("_"):
                self.load_extension(f"src.cogs.{filename}")
            elif not filename.startswith("_"):
                self.load_extension(f"src.cogs.{filename[:-3]}")
        self.load_extension("jishaku")

    def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        path = name.replace(".", "/")
        if os.path.isdir(path):
            for root, dir_, files in os.walk(path):
                for file in files:
                    if not file.startswith("_") and file.endswith(".py"):
                        try:
                            super().load_extension(
                                os.path.join(root, file)
                                .replace("\\", "/")
                                .replace("/", ".")[:-3]
                            )
                        except Exception as e:
                            if not str(e).endswith("has no 'setup' function."):
                                print(e)
            return
        super().load_extension(name, package=package)

    def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        path = name.replace(".", "/")
        if os.path.isdir(path):
            for root, dir_, files in os.walk(path):
                for file in files:
                    if not file.startswith("_") and file.endswith(".py"):
                        try:
                            super().load_extension(
                                os.path.join(root, file)
                                .replace("\\", "/")
                                .replace("/", ".")[:-3]
                            )
                        except Exception as e:
                            if not str(e).endswith("has no 'setup' function."):
                                print(e)
            return
        super().unload_extension(name, package=package)

    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def connect_database(self):
        self.db = await aiosqlite.connect('./db/database.db')

    async def on_message(self, original_message: disnake.Message) -> None:
        # Prevent bots from executing commands
        if original_message.author.bot or "jarvide" not in original_message.content.lower():
            return

        message_content = "".join(
            [char for char in original_message.content.lower() if char not in string.punctuation]
        )

        message_content = " ".join(
            word for word in message_content.split() if word != "jarvide"
        )

        list_of_commands = {c: [c.name, *c.aliases] for c in self.commands}

        commands_in_message = list(filter(
            lambda c: any([x in message_content.split() for x in c[1]]),
            list_of_commands.items()
        ))

        if len(commands_in_message) != 1:           
            return  # TODO: Maybe make the user know that they supplied too many commands?

        cmd = commands_in_message[0][0]
        ctx = await super().get_context(original_message)
        userAuthorized = await cmd.can_run(ctx)             

        if userAuthorized:
            args = original_message.content.partition(
                [i for i in list_of_commands[cmd] if i in original_message.content.lower()][0]
            )[2]

            new_message = copy.copy(original_message)
            new_message.content = f"jarvide {cmd.name} {args}"
            await super().process_commands(new_message)

    async def on_ready(self) -> None:
        self.send_guild = self.get_guild(926811692019626064)
        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
