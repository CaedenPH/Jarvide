import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=["hey jarvide, ", "hey jarvide", "jarvide, "], help_command=None)


# on ready event 
@bot.event
async def on_ready():
    print("jarvide is ready")
