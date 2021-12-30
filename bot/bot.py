import disnake
from disnake.ext.commands import Bot

bot = Bot(command_prefix=['hey jarvis, ', 'hey ', '!'], help_command=None)

@bot.command()
async def on_ready():
    print('Jarvide is ready.')


@bot.command()
async def ping(ctx):
    if round(bot.latency * 1000) > 150:
        health = "Unhealthy"
        color = disnake.Color.red()
    elif round(bot.latency * 1000) in range(70,99):
        health = "Unhealthy"
        color = disnake.Color.yellow()
    else:
        health = "Healthy"
        color = disnake.Color.green()
    embed1=disnake.Embed(color=color)
    embed1.add_field(name="**Latency**",value=f"```{round(bot.latency * 1000)} ms```")
    embed1.add_field(name="**Health**",value=f"```{health}```")
    embed1.set_footer(text="Discord API issues could lead to high latency times")
    await ctx.send(content="🏓**Pong**",embed=embed1)


bot.run(TOKEN)
