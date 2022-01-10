import disnake
import typing
from disnake.ext import commands
from disnake.ext.commands import Context


class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def blacklist(self, ctx: Context):
        if ctx.subcommand is None:
            return await ctx.send("Provide a subcommand to run blacklist")
    

    @blacklist.command()
    async def user(self, ctx: Context, user: disnake.User):
        ... # add user to blacklist

    @blacklist.command()
    async def remove_user(self, ctx: Context, user: disnake.User):
        ... # remove user from blacklist

