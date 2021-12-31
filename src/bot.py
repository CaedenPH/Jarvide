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
        if message.author.bot:
            return 
        
        message.content = ''.join(list(filter(lambda m: m in string.ascii_letters or m.isspace(), message.content)))
        for command_name in [k.name for k in self.commands]:
            if command_name in message.content.lower().split():
                message.content = "jarvide " + command_name 
                break

        return await super().on_message(message)

    async def on_ready(self) -> None:
        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
