import disnake
import os

from .HIDDEN import TOKEN
from .utils import REMOVE_WORDS

from disnake.ext import commands

class Jarvide(commands.Bot):
    def __init__(self):
        super().__init__(

            command_prefix = "jarvide",
            case_insensitive = True,
            strip_after_prefix = True,
            help_command = None,
            intents=disnake.Intents.all(),
            owner_ids = [298043305927639041]

        )
    
    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.startswith("_"):
                self.load_extension(f"src.cogs.{filename[:-3]}")
        self.load_extension("jishaku")

    def parse_message(self, message: disnake.Message) -> str:
        content = message.content.lower()

        if "jarvide" in content:
            for word in REMOVE_WORDS:
                content = content.replace(
                    word + " " if len(word) >= 2 else word, ""
                )
            return f"jarvide {content}"
        return message.content
    
    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot:
            return 

        message.content = self.parse_message(message)
        return await super().on_message(message)

    async def on_ready(self) -> None:
        guild = self.get_guild(926115595307614249)
        role = guild.get_role(926115630497800193)

        for k in role.members:
            self.owner_ids.append(k.id)

        print("Set up")

    async def on_command_error(self, ctx, error):
        await ctx.send(error)



