import disnake
from disnake.ext.commands import Bot

bot = Bot(command_prefix=['hey jarvis, ', 'hey ', '!'], help_command=None)

@bot.command()
async def on_ready():
    print('Jarvide is ready.')

@bot.command()
async def ping(ctx):
    await ctx.send(f'{bot.latency*1000: .2f}')

bot.run(TOKEN)
