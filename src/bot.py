import disnake
import os
import string
import copy
import aiosqlite

from typing import Optional

from .HIDDEN import TOKEN
from disnake.ext import commands


class Jarvide(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,
            intents=disnake.Intents.all(),
        )

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
        message = copy.copy(original_message)
        self.channel = self.get_channel(926811692019626067)

        if message.author.bot:
            return

        if "jarvide" not in message.content.lower():
            return

        commands_ = [k.name for k in self.commands]
        for command in self.commands:
            if not command.aliases:
                continue
            for alias in command.aliases:
                commands_.append(alias)

        message.content = "".join(
            list(
                filter(
                    lambda m: m in string.ascii_letters or m.isspace(), message.content
                )
            )
        )
        for command_name in commands_:
            if command_name in message.content.lower().split():
                message.content = (
                    "jarvide "
                    + command_name
                    + " ".join(original_message.content.split(command_name)[1:])
                )
                break
        return await super().on_message(message)

    async def on_ready(self) -> None:
        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
