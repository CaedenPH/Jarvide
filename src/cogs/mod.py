import disnake
import typing

import time_str
from disnake.ext import commands
from disnake.ext.commands import Context

from src.utils.confirmation import prompt


class Mod(commands.Cog):
    """Moderation related commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🔨"
        self.short_help_doc = self.__doc__

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: Context,
        member: disnake.Member = None,
        reason: str = "No Reason Provided.",
    ):
        """ Kicks a member from a guild """
        if not member:
            return await ctx.send(
                f"{ctx.author.mention}, please provide a member to kick."
                )

        elif member == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot kick yourself!")

        choice = await prompt(
            ctx, message="Are you sure you want to kick this user?", timeout=60
            )

        if choice:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked.")
        else:
            await ctx.send(f"Cancelled kick.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context,
        member: disnake.Member = None,
        reason="No Reason Provided.",
    ):
        """ Bans a member outside of a guild """
        if not member:
            return await ctx.send(f"{ctx.author.mention}, please provide a member to ban.")

        elif member == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot ban yourself!")

        choice = await prompt(
            ctx, message="Are you sure you want to ban this user?", timeout=60
            )
        if choice:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned.")
        else:
            await ctx.send(f"Cancelled ban.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: Context,
        user: typing.Union[disnake.User, int] = None,
        reason="No Reason Provided.",
    ):
        """ unbans someone from a guild """
        if not user:
            return await ctx.send(
                f"{ctx.author.mention}, please provide an ID of a user to unban."
                )

        elif user == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot unban yourself!")

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

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: Context, channel: disnake.TextChannel = None, slowmode: int = None):
        """Change/disable slowmode in a channel"""
        channel = channel or ctx.channel
        if not slowmode:
            return await ctx.send(
                f"{ctx.author.mention}, please provide a number to set the slowmode to."
            )
        else:
            await channel.edit(slowmode_delay=slowmode)
            return await ctx.send(
                f"I've set the channel slowmode to {slowmode} {'seconds' if slowmode > 1 else 'second'}."
                )

    @commands.command(aliases=["mute", "to", "silence", "shush"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: disnake.Member, time: str, *, reason=None):
        """ timesout (or mute) a member from a guild """
        now = disnake.utils.utcnow()
        change = time_str.convert(time)
        duration = now + change
        await member.timeout(until=duration, reason=reason)
        await member.send(
            f"You have been timed out from: {ctx.guild.name}, until <t:{int(duration.timestamp())}:f>"
        )
        await ctx.send(
            embed=disnake.Embed(
                title="Timed Out!",
                description=(
                    f"{member.mention} was timed out until <t:{int(duration.timestamp())}:f> for reason: {reason}"
                    ),
                color=disnake.Colour.green(),
                )
            )

    @commands.command(aliases=["unsilence"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: disnake.Member, *, reason):
        """ unmutes a member (or removes timeout) from a guild """
        await member.timeout(until=None, reason=reason)
        await ctx.send(
            embed=disnake.Embed(
                title="unmuted", description=f"{member.mention} was unmuted."
                )
            )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, *, member: disnake.Member, *, role: disnake.Role, *, reason="No Reason Provided."):
        await member.add_roles(role,reason=reason)
        await ctx.send(f"I gave the {role} role to {member.name}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Mod(bot))
