import disnake
import os
import string
import copy
import aiosqlite
import re
import timeit

from typing import Optional

from disnake.ext.commands.core import command

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
        if original_message.author.bot:
            return

        # Prevent the bot from running commands if its name is never mentioned
        if "jarvide" not in original_message.content.lower():
            return super().on_message(original_message)

        # Stripping all of the "punctuation" characters out of the message
        messageContent = "".join(
            [char for char in original_message.content.lower() if char not in string.punctuation]
        )

        # IDE command interferes with the jarvide prefix
        # NOTE: This is what you'd replace if you were making another `REMOVE_WORDS` thing.
        messageContent = " ".join(
            word for word in messageContent.split() if word != "jarvide"
        )

        # Create a dictionary for command lookup that also includes aliases (if any are present)
        listOfCommands = {c : [c.name, *c.aliases] for c in self.commands}

        # Get a list of all of the command keywords that the user mentioned in their message
        commandsInMessage = list(filter(
            lambda c: any([x in messageContent.split() for x in c[1]]), 
            listOfCommands.items()
        ))

        # Ensure that only one command is going to be ran.
        if len(commandsInMessage) != 1:                     
            return await super().on_message(original_message)

        cmd = commandsInMessage[0][0]                       # Get the actual command object
        ctx = await super().get_context(original_message)   # Get the context from the message
        userAuthorized = await cmd.can_run(ctx)             

        if userAuthorized:                                  # Ensure the user can actually run the command

            # Grabbing all of the arguments after the used alias                              
            args = messageContent.partition(
                [i for i in listOfCommands[cmd] if i in messageContent][0]
            )[2]

            # Invoke the actual command
            await ctx.invoke(
                cmd,
                *args.split()[:len(cmd.clean_params)]       # Only allowing the user to pass as many args as the function allows
            )

    async def on_ready(self) -> None:
        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
