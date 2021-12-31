import disnake
import os
import string

from .HIDDEN import TOKEN
from disnake.ext import commands

class Jarvide(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,
            intents=disnake.Intents.all()
        )
    
    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.startswith("_"):
                self.load_extension(f"src.cogs.{filename[:-3]}")
        self.load_extension("jishaku")

    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def on_message(self, message: disnake.Message) -> None:
        self.channel = self.get_channel(926537964249559060)

        if message.author.bot:
            return 
        
        if "jarvide" not in message.content.lower():
            return 
        commands = [k.name for k in self.commands]
        for command in self.commands:
            if not command.aliases:
                continue
            for alias in command.aliases:
                commands.append(alias)

        message.content = ''.join(list(filter(lambda m: m in string.printable, message.content)))
        for command_name in commands:
            if command_name in message.content.lower().split():
                # For anyone confused, this rearranges the user-provided input into how it would be normally,
                # becuase this bot is desinged so you can talk to it normally, the commands won't normally be in the
                # [PREFIX] [COMMAND NAME] [ARGS] format. It's up to us to rearrange it so it is in that format
                message.content = "jarvide " + command_name + ' '.join(message.content.split(command_name)[1:])
                break

        await self.process_commands(message)

    async def on_ready(self) -> None:
        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
