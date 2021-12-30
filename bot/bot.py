import disnake
from disnake.ext.commands import Bot, Context, command

class Jarvide(Bot):
    def __init__(self, *args, **kwargs) -> None:

        # Initialize the parent class
        super().__init__(
            command_prefix=['hey jarvis, ', 'hey ', '!'],
            help_command=None
        )

        # Setup the basic commands
        self.add_listener(self.readyListener, "on_ready")
        self.add_command(self._ping)

    async def readyListener(self, *args, **kwargs) -> None:
        """Logs when the bot is ready"""
        print(
            "Jarvide is ready."
        )

    @command(name="ping")
    async def _ping(ctx):
        jarvisLatency = round(bot.latency * 1000)

        return await ctx.send(
            embed = disnake.Embed(
                title = "Pong!",
                description = f"Jarvis ping: **{jarvisLatency}ms**\n**Health:** {'healthy' if jarvisLatency < 150 else 'unhealthy'}",
                color = disnake.Color.yellow()
            )
        )

if __name__ == "__main__":
    bot = Jarvide()
    bot.run(
        TOKEN
    )
