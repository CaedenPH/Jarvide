import disnake
import typing

from disnake.ext import commands

from src.utils.confirmation import prompt


class Mod(commands.Cog):
    """Mod cog for moderation related commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: commands.Context,
        member: disnake.Member = None,
        reason: str = "No Reason Provided.",
    ):
        if not member:
            return await ctx.send(
                f"{ctx.author.mention}, please provide a member to kick."
            )

        choice = await prompt(
            ctx, message="Are you sure you want to kick this user?", timeout=60
        )
        if choice:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked.")
        else:
            await ctx.send(f"Cancelled kick.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: commands.Context,
        member: disnake.Member = None,
        reason="No Reason Provided.",
    ):
        if not member:
            await ctx.send(f"{ctx.author.mention}, please provide a member to ban.")
            return

        choice = await prompt(
            ctx, message="Are you sure you want to ban this user?", timeout=60
        )
        if choice:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned.")
        else:
            await ctx.send(f"Cancelled ban.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: commands.Context,
        user: typing.Union[disnake.User, int] = None,
        reason="No Reason Provided.",
    ):
        if not user:
            await ctx.send(
                f"{ctx.author.mention}, please provide an ID of a user to unban."
            )
            return

        choice = await prompt(
            ctx, message="Are you sure you want to ban this user?", timeout=60
        )
        if choice:
            await ctx.guild.unban(
                user if isinstance(user, disnake.User) else disnake.Object(user),
                reason=reason,
            )
            await ctx.send("Successfully unbanned that user.")
        else:
            await ctx.send("Cancelled the unban")


def setup(bot: commands.Bot) -> None:
    """Setup mod cog"""
    bot.add_cog(Mod(bot))
