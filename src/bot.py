import disnake
import os

from disnake.ext import commands

REMOVE_WORDS = [
    'please',
    'tell',
    'me',
    'jarvide',
    ','
    ]

class Jarvide(commands.Bot):
    TOKEN = "OTI2MTIyMDY1OTczNjE2Njkw.Yc3EYw.98P2SO0CS8JHXCDp0oDzhPiZ-OM"

    def __init__(self):
        super().__init__(

            command_prefix = "jarvide",
            case_insensitive = True,
            strip_after_prefix = True,
            help_command = None,
            intents=disnake.Intents.all(),

        )
    
    def setup(self) -> None:
        for filename in os.listdir('./src/cogs'):
            if not filename.startswith('_'):
                self.load_extension(f"src.cogs.{filename[:-3]}")


    def parse_message(self, message: disnake.Message) -> str:
        content = message.content.lower()

        if "jarvide" in content:
            for word in REMOVE_WORDS:
                content.replace(
                    word, ''
                )
            return f"jarvide {content}"
        return message.content
    
    def run(self) -> None:
        self.setup()
        super().run(self.TOKEN, reconnect=True)

    async def on_message(self, message: disnake.Message) -> None:
        message.content = self.parse_message(message)
        return await super().on_message(message)

    async def on_ready(self) -> None:
        guild = self.get_guild(926115595307614249)
        role = guild.get_role(926115630497800193)
        
        for k in role.members:
            self.owner_ids.append(k.id)



