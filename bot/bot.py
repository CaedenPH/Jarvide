import disnake
from disnake.ext.commands import Bot

bot = Bot(command_prefix=['hey jarvis, ', 'hey ', '!'], help_command=None)

@bot.command()
async def on_ready():
    print('Jarvide is ready.')


@bot.command()
async def ping(ctx):
    if round(bot.latency * 1000) > 150:
        health = "unhealthy"
    else:
        health = "healthy"
    ping_embed = disnake.Embed(
        title="Pong!",
        description=f"Jarvide ping: **{round(bot.latency * 1000)}ms** \n**health**: \n {health}",
        color=disnake.Color.yellow()
    )
    await ctx.send(embed=ping_embed)


bot.run(TOKEN)
