from __future__ import annotations

import disnake
import time_str

from disnake import Embed, Member
from disnake.ext import commands
from disnake.ext.commands import Context, Greedy
from typing import Union

from src.utils.confirmation import prompt

from ..bot import Jarvide

mutedUserIDs = []

class ParseError(Exception):
    """Could not parse item"""

class Mod(commands.Cog):
    """Moderation related commands."""

    def __init__(self, bot: Jarvide) -> None:
        self.bot = bot
        self.emoji = "🔨"
        self.short_help_doc = self.__doc__

    def parse(self, content: str) -> int:
        """Parse time like 1h into seconds"""

        numbers = ''.join(list(filter(lambda m: not m.isalpha(), content)))
        letters = ''.join(list(filter(lambda m: m.isalpha(), content)))

        duration = [char for char in letters if char in ['s', 'm', 'h']]
        seconds = numbers

        if not duration:
            seconds = int(numbers)
        if len(duration) >= 2:
            raise ParseError()  
        
        duration = ''.join(duration)
        if duration == "s":
            seconds = int(seconds) * 1
        elif duration == "m":
            seconds = int(seconds) * 60
        elif duration == "h":
            seconds = int(seconds) * 3600
        return seconds
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setnick(self, ctx: Context, member: disnake.Member, *, nick):
        """
        Set a custom nick-name.
        """
        if not ctx.author.top_role.position > member.top_role.position:
            return await ctx.send("You cant change someone's nickname that is higher or the same role heirarchy.")
        await member.edit(nick=nick)
        await ctx.send(f"Nickname for {member.name} was changed to {member.mention}", delete_after=12)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx: Context,
        channel: Greedy[disnake.TextChannel] = None,
        slowmode: str = None,
    ):
        """Change/disable slowmode in a channel"""

        channel = channel or ctx.channel
        if slowmode is None:
            return await ctx.send(
                f"{ctx.author.mention}, please provide a number to set the slowmode as or 0 to remove the slowmode."
            )
        
        try:
            seconds = self.parse(slowmode)
        except ParseError:
            return await ctx.send(
                f"{ctx.author.mention}, you did not specify your seconds in the correct format. Try a format like 12s"
            )

        if seconds <= 0:
            seconds = 0
        
        if not isinstance(channel, list):
            await channel.edit(slowmode_delay=seconds)
        else:
            for editchannel in channel:
                await editchannel.edit(slowmode_delay=seconds)
        
        if slowmode == 0:
            return await ctx.send(f"I've reset the slowmode in {channel}")
        await ctx.send(
            f"I've set the channel's slowmode to {seconds} {'seconds' if seconds > 1 else 'second'}."
        )



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

    @commands.command(aliases=["mute", "silence", "shush"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: disnake.Member, time: str, *, reason=None):
        """timesout (or mute) a member from a guild"""
        now = disnake.utils.utcnow()
        change = time_str.convert(time)
        duration = now + change
        if member.id in mutedUserIDs:
            await ctx.send(embed=Embed(
                title = "Error",
                description = f"{member.mention} is already timed out!" ,
                color = 0x850101
            ))
            return
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
        mutedUserIDs.append(ctx.author.id)

    @commands.command(aliases=["unsilence"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: Context, member: disnake.Member, *, reason=None):
        """unmutes a member (or removes timeout) from a guild"""
        await member.timeout(until=None, reason=reason)
        if member.id in mutedUserIDs:
            await ctx.send(
            embed = Embed(
                    title="Unmuted!",
                    description=f"`{member.mention}` ({member.id}) has been unmuted by `{ctx.author.name}`",
                    color=0x00FF00
                ).set_footer(
                    text=f"This command was issued by `{ctx.author.name}`",
                    icon_url=ctx.author.display_avatar.url
                    )
            )
            mutedUserIDs.remove(member.id)
        return await ctx.send(
            embed=Embed(
                title = "Error",
                description = f"{ctx.author.name} is not muted!",
                color = 0x850101
            ).set_footer(
                text = f"requested by {ctx.author.name}",
                icon_url = ctx.author.display_avatar.url
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


def setup(bot: Jarvide) -> None:
    bot.add_cog(Mod(bot))
