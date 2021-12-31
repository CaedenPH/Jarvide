import disnake

from disnake.ext import commands


class Mod(commands.Cog):
    """Mod cog for moderation related commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self,ctx,member: disnake.Member=None, reason="No Reason Provided."):
        if not member:
            await ctx.send(f"{ctx.author.mention}, please provide a member to kick.")
        else:
            await ctx.send(f"{ctx.author.mention}, please reply with __**YES**__ if you want to kick {member}, or please reply with __**NO**__ if you changed your mind.")
            def check(m):
                return ctx.author == m.author and m.content.lower() == "yes" or m.content.lower() == 'no'
            try:
                reply = await self.bot.wait_for('message',check=check,timeout=60)
                if reply.content.lower() == "yes":
                    await ctx.send(f"{member.mention}, has been kicked.")
                    await member.kick(reason=reason)
                elif reply.content.lower() == "no":
                    await ctx.send("Cancelled kick.")
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, you didn't reply in time so I cancelled the kick.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self,ctx,member: disnake.Member=None, reason="No Reason Provided."):
        if not member:
            await ctx.send(f"{ctx.author.mention}, please provide a member to ban.")
        else:
            await ctx.send(f"{ctx.author.mention}, please reply with __**YES**__ if you want to ban {member}, or please reply with __**NO**__ if you changed your mind.")
            def check(m):
                return ctx.author == m.author and m.content.lower() == "yes" or m.content.lower() == 'no'
            try:
                reply = await self.bot.wait_for('message',check=check,timeout=60)
                if reply.content.lower() == "yes":
                    await ctx.send(f"{member.mention}, has been banned. Deleted `2` days of messages.")
                    await member.ban(delete_message_days = 2,reason=reason)
                elif reply.content.lower() == "no":
                    await ctx.send("Cancelled ban.")
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, you didn't reply in time so I cancelled the ban.")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self,ctx,id: int=None, reason="No Reason Provided."):
        if not id:
            await ctx.send(f"{ctx.author.mention}, please provide a member to unban.")
        else:
            await ctx.send(f"{ctx.author.mention}, please reply with __**YES**__ if you really want to unban, or please reply with __**NO**__ if you changed your mind.")
            def check(m):
                return ctx.author == m.author and m.content.lower() == "yes" or m.content.lower() == 'no'
            try:
                reply = await self.bot.wait_for('message',check=check,timeout=60)
                if reply.content.lower() == "yes":
                    await ctx.send("successfully unbanned")
                    await ctx.guild.unban(id,reason=reason)
                elif reply.content.lower() == "no":
                    await ctx.send("Cancelled unban.")
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, you didn't reply in time so I cancelled the unban.")


def setup(bot: commands.Bot) -> None:
    """Setup mod cog"""
    bot.add_cog(Mod(bot))
