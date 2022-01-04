import discord
from discord.bot import ApplicationCommandMixin 
from discord.ext import commands
import aiosqlite

class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.group(aliases = ['config'])
    @commands.has_permissions(administrator = True)
    async def configure(self, ctx):
        if ctx.invoked_with == None:
            return await ctx.reply(f"Invalid usage... Use {ctx.prefix}help configure")

    @configure.command()
    @commands.has_permissions(administrator = True)
    async def allowchannel(self, ctx, channel: discord.TextChannel):
        async with aiosqlite.connect("databases/config.sqlite") as db:
            async with db.cursor() as cur:
                guilds = (i[0] for i in await cur.execute("SELECT * FROM guilds"))
                if ctx.guild.id not in guilds:
                    await cur.execute("INSERT INTO guilds (id, allowedChannels) VALUES (%s, %s)" % (ctx.guild.id, (ctx.guild.system_channel, channel.id))
                else:
                    await cur.execute(f"UPDATE guilds SET allowedChannels = (allowedChannels, {channel.id}) WHERE guildid = {ctx.guild.id}")
                await cur.commit()
                await ctx.reply(embed = discord.Embed(title = f"Added.", description = f"The channel {channel} Was successfully added to the allowed list"))
                return       


def setup(bot):
    bot.add_cog(Config(bot))
