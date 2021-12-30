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
        color = "disnake.Color.red()
    elif round(bot.latency * 1000) in range(70,99):
        health = "unhealthy" 
        color = disnake.Color.yellow()
    else:
        health = "healthy"
        color = disnake.Color.green()
    ping_embed = disnake.Embed(
        title="Pong!",
        description=f"Jarvide ping: **{round(bot.latency * 1000)}ms** \n**health**: \n {health}",
        color=color
    )
    await ctx.send(embed=ping_embed)


bot.run(TOKEN)
