from __future__ import annotations
from os import name
import aiohttp

import disnake
import time_str

from disnake.ext import commands
from disnake.ext.commands import Context, Greedy
from typing import Union

from src.utils.confirmation import prompt

from decouple import config


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
        member: disnake.Member,
        reason: str = "No Reason Provided.",
    ):
        """Kicks a member from a guild"""

        if member == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot kick yourself!")

        if (
            ctx.author.top_role.position <= member.top_role.position
            and ctx.author.id != ctx.guild.owner_id
        ):  # checking role hierarchy
            return await ctx.send(f"{ctx.author} You can't kick **{member.name}**")

        choice = await prompt(
            ctx, message="Are you sure you want to kick this user?", timeout=60
        )

        if choice:
            try:
                await member.kick(reason=reason)
                await ctx.send(f"{member.mention} has been kicked.")
            except disnake.Forbidden:
                await ctx.reply(
                    f"Unable to kick **{member.name}** due to role hierarchy"
                )
        else:
            await ctx.send("Cancelled kick.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context,
        member: disnake.Member,
        reason="No Reason Provided.",
    ):
        """Bans a member outside of a guild"""

        if member == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot ban yourself!")

        if (
            ctx.author.top_role.position <= member.top_role.position
            and ctx.author.id != ctx.guild.owner_id
        ):  # checking role hierarchy
            return await ctx.send(f"{ctx.author} You can't ban **{member.name}**")

        choice = await prompt(
            ctx, message="Are you sure you want to ban this user?", timeout=60
        )
        if choice:
            try:
                await member.ban(reason=reason)
                await ctx.send(f"{member.mention} has been banned.")
            except disnake.Forbidden:
                await ctx.reply(
                    f"Unable to ban **{member.name}** due to role hierarchy"
                )
        else:
            await ctx.send("Cancelled ban.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: Context,
        user: Union[disnake.User, int],
        reason="No Reason Provided.",
    ):
        """unbans someone from a guild"""

        if user == ctx.author:
            return await ctx.send(f"{ctx.author.mention}, you cannot unban yourself!")

        choice = await prompt(
            ctx, message="Are you sure you want to unban this user?", timeout=60
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
    async def slowmode(
        self,
        ctx: Context,
        channel: Greedy[disnake.TextChannel] = None,
        slowmode: int = None,
    ):
        """Change/disable slowmode in a channel"""
        channel = channel or ctx.channel
        if slowmode is None:
            return await ctx.send(
                f"{ctx.author.mention}, please provide a number to set the slowmode as or 0 to remove the slowmode."
            )
        for editchannel in channel:
            await editchannel.edit(slowmode_delay=slowmode)
        if slowmode == 0:
            return await ctx.send("I've reset the channel's slowmode")
        else:
            return await ctx.send(
                f"I've set the channel's slowmode to {slowmode} {'seconds' if slowmode > 1 else 'second'}."
            )

    @commands.command(aliases=["mute", "silence", "shush"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: disnake.Member, time: str, *, reason=None):
        """timesout (or mute) a member from a guild"""
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
    async def unmute(self, ctx, member: disnake.Member, *, reason=None):
        """unmutes a member (or removes timeout) from a guild"""
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
    async def role(
        self,
        ctx,
        member: disnake.Member,
        role: disnake.Role,
        *,
        reason="No Reason Provided.",
    ):
        """Add a role to the user"""
        if ctx.author.top_role.position <= role.position:
            return await ctx.send("You cannot add that role to someone!")
        try:
            await member.add_roles(role, reason=reason)
        except disnake.Forbidden:
            return await ctx.send(f"Unable to add that role to {member.name}")
        await ctx.send(f"I gave the {role} role to {member.name}.")


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def warn(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        *,
        reason="No reason provided."
    ):
        """ Warns the given user. """

        await self.bot.jarvide_api_session.post('/warns', data={
            "userID": member.id,
            "modID": ctx.author.id,
            "reason": reason
        })

        await ctx.send(f"Warned {member.mention}.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def warnings(
        self,
        ctx: commands.Context,
        member: disnake.Member
    ):
        """ Gets all warnings for the given user. """

        async with self.bot.jarvide_api_session.get('warns', params={
            "userID": member.id
        }) as r:
            embed = disnake.Embed(
                title=f'Warnings for {member}',
                color=disnake.Color.blue()
            )

            for warn in r:
                json = await r.json()
                embed.add_field(
                    name=json['warnID'],
                    value=f"Moderator: {ctx.guild.get_member(json['modID'])}\nReason: {json['reason']}",
                    inline=False
                )


        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def delwarn(
        self,
        ctx: commands.Context,
        warnID: str
    ):
        r = await self.bot.jarvide_api_session.delete('warns', params={
            "warnID": warnID
        })

        if(r.status == 404):
            await ctx.send('Invalid warn ID.')
            return

        await ctx.send('Warn was successfully deleted.')

    @commands.command()
    @commands.guild_only()
    async def whois(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Whois {member.name}",timestamp=ctx.message.created_at,description=f"Here is some information about {member.mention}.")
        embed.set_thumbnail(url=member.avatar_url)
        joined_at = disnake.utils.format_dt(member.joined_at)
        created_at = disnake.utils.format_dt(member.created_at)
        embed.add_field(name=f"📆 Joined {ctx.guild} at:", value=joined_at, inline=False)
        embed.add_field(name="📆 Account created at:", value=created_at, inline=False)
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="🔢 Join position", value=str(members.index(member)+1), inline=False)
        role_string = ' '.join([r.mention for r in member.roles][1:])
        embed.add_field(name=f"📜 Roles [{len(member.roles)-1}]", value=f"{role_string if len(member.roles) > 1 else "member has no roles."}", inline=False)
        embed.add_field(name=f"🆔 member ID:",value=f"{member.id}", inline=False)
        if str(member.status) == "dnd":
            embed.add_field(name=f"<:status:838834549064466432> Status:",value=f"<:dnd:838833690787577900> Do Not Disturb", inline=False)
        elif str(member.status) == "online":
            embed.add_field(name=f"<:status:838834549064466432> Status:",value=f"<:online:838833901660799017> Online", inline=False)
        elif str(member.status) == "idle":
            embed.add_field(name=f"<:status:838834549064466432> Status:",value=f"<:idle:838833627076100136> Idle", inline=False)
        elif str(member.status) == "offline":
            embed.add_field(name=f"<:status:838834549064466432> Status:",value=f"<:invisible:838833583828238338> Offline", inline=False)
        await ctx.send(embed=embed)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Mod(bot))
