import os
import string
import copy
import disnake

from disnake.ext import commands
import aiosqlite
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from .HIDDEN import TOKEN, MONGO_URI


class Jarvide(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="jarvide",
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=None,  # type: ignore
            intents=disnake.Intents.all(),
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

    async def on_message(self, original_message: disnake.Message) -> None:
        # Prevent bots from executing commands
        if (
            original_message.author.bot
            or "jarvide" not in original_message.content.lower()
        ):
            return

        message_content = "".join(
            [
                char
                for char in original_message.content.lower()
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

        if len(commands_in_message) != 1:
            return  # TODO: Maybe make the user know that they supplied too many commands?

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
            new_message.content = f"jarvide {cmd.name} {args}"
            await super().process_commands(new_message)

    async def on_ready(self) -> None:
        self.send_guild = self.get_guild(926811692019626064)
        print("Set up")
    
    async def on_guild_join(guild)
        await guild.system_channel.send(embed = disnake.Embed(title = f"Thank you for adding my bot!", description = f"""
        Hello, i am jarvide Bot And IDE ```yaml\nHow to use Ide command:

        To start: run the command; [jarvide ide]

Note:
    - all phases have an exit button; to open a new IDE, you have to exit your open ide. (one ide open per channel)

Creating a file (OpenFile phase):
    - press the create button 
       ➥ enter a filename; 
            [must be shorter than 12 characters long.]
            [if you want to run the file, you must put the file extension. eg if you want it to be ran in python, you put .py in the filename]
       ➥ enter the content;
            [you can use discord codeblocks if you want]
            [this can be edited and changed]

    + you have just created a file. You have now moved onto the FileView phase!
    + you can also open files via    links, uploading, github and saved files 
        ➥ [ supported links are (toptal, pastebin, ghostbin)]'n```"""))
        async with aiosqlite.connect("databases/config.db") as db:
            async with db.cursor() as cur:
                guilds = (i[0] for i in await cur.execute("SELECT * FROM guilds"))
                if guild.id not in guilds:
                    await cur.execute("INSERT INTO guilds (id, allowedChannels) VALUES (%s, %s)" % (guild.id, (ctx.guild.system_channel)
                else: return
                await cur.commit()  

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
