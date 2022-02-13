import os
import string
import copy
import typing
import aiohttp

from disnake import Message, AllowedMentions, Intents
from disnake.ext.commands import (
    Bot
)
from disnake.utils import find
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from src.utils.utils import main_embed
from .HIDDEN import TOKEN, MONGO_URI
from decouple import config

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
            allowed_mentions=AllowedMentions(everyone=False, roles=False),
        )
        self.engine = AIOEngine(AsyncIOMotorClient(MONGO_URI))
        self.send_guild = None
        self.error_channel = None
        self.server_message = None
        self.bugs = range(10000, 100000)
        self.http_session = aiohttp.ClientSession()
        self.jarvide_api_session = aiohttp.ClientSession(f"http://{config('BASE_URL')}", headers={"Api-Key": config("JARVIDE_API_KEY")})

    def setup(self) -> None:
        for filename in os.listdir("./src/cogs"):
            if not filename.startswith("_") and filename.endswith("py"):
                self.load_extension(f"src.cogs.{filename[:-3]}")

        self.load_extension("src.cogs.ide.ide")
        self.load_extension("src.cogs.ide.auto_detect")
        self.load_extension("jishaku")

    def run(self) -> None:
        self.setup()
        super().run(TOKEN, reconnect=True)

    async def request(self, method: str, url: str, **kwargs):
        return await self.http_session.request(method, "https://api.github.com" + url, **kwargs)

    async def on_message(self, original_message: Message) -> typing.Optional[Message]:
        new_msg = copy.copy(original_message)
        new_message = copy.copy(original_message)
        if new_msg.content in [f"<@!{self.user.id}>", f"<@{self.user.id}>"]:
            return await new_msg.channel.send(embed=main_embed(self))
        if new_msg.author.bot or "jarvide" not in new_msg.content.lower():
            return
        new_msg.content = " ".join(
            [
                word
                for word in new_msg.content.lower().split()
                if not any(
                    word.startswith(censored_word) for censored_word in REMOVE_WORDS
                )
            ]
        )
        new_msg.content = "".join(
            [
                char
                for char in new_msg.content
                if (char in string.ascii_letters or char.isspace() or char == '8')
            ]
        )
        message_content = " ".join(
            word for word in new_msg.content.split() if word != "jarvide"
        )
        list_of_commands = {c: [c.name, *c.aliases] for c in self.commands}
        commands_in_message = list(
            filter(
                lambda c: any([x in message_content.split() for x in c[1]]),
                list_of_commands.items(),
            )
        )
        commands_in_message.reverse()
        if len(commands_in_message) <= 0:
            return

        if "help" in [k[0].name for k in commands_in_message] and commands_in_message[0][0].name != "help":
            commands_in_message = commands_in_message[::-1]

        cmd = commands_in_message[0][0]
        args = new_message.content.partition(
            [i for i in list_of_commands[cmd] if i in new_msg.content.lower()][0]
        )[2]
        new_message = copy.copy(new_msg)
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
        channel = find(lambda i: i.name in names, guild.channels)
        if channel != None:
            return await channel.send(embed = embed)
        try:
            await guild.system_channel.send(embed=embed)
        except AttributeError:
            pass  
