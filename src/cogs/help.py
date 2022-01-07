from collections.abc import Mapping

from disnake import utils, Embed, Color, MessageInteraction, SelectOption
from disnake.ui import View, Select
from disnake.ext.commands import Bot, Command, Cog, command, HelpCommand, Context, Group
from typing import Optional, List


class HelpCog(Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = JarvideHelp()
        bot.help_command.cog = self

    @command(name="h", hidden=True)
    async def help_alias(self, ctx: Context, *, arg=None):
        if arg:
            await ctx.send_help(arg)
        else:
            await ctx.send_help()


def setup(bot: Bot):
    bot.add_cog(HelpCog(bot))


class JarvideHelp(HelpCommand):
    def __init__(self):
        super().__init__()

    async def command_callback(self, ctx, *, cmd=None):
        """
        Override to make the help for Cog case-insensitive
        """
        await self.prepare_help_command(ctx, cmd)
        bot = ctx.bot

        if cmd is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = None
        _cog = [cog for cog in ctx.bot.cogs if cog.lower() == cmd.lower()]
        if _cog:
            cog = _cog[0]
        if cog is not None:
            return await self.send_cog_help(ctx.bot.get_cog(cog))

        maybe_coro = utils.maybe_coroutine

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = cmd.split(" ")
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            string = await maybe_coro(
                self.command_not_found, self.remove_mentions(keys[0])
            )
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(
                    self.subcommand_not_found, cmd, self.remove_mentions(key)
                )
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(
                        self.subcommand_not_found, cmd, self.remove_mentions(key)
                    )
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)

    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command]]):
        """
        Bot's Help Command ,
        Views from the HelpView() class
        TO-DO : Invite Button and URL , Change Help Command interface with SHort help text
        """
        _bot: Bot = self.context.bot

        embed = Embed(
            color=Color.og_blurple(),
            description=_bot.description
            + f"```fix\nPrefix : {await _bot.get_prefix(self.context.message)}```",
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/926115595307614252/927951464725377034/big.png"
        )
        for cog_name in _bot.cogs:
            if cog_name.lower() in ("jishaku", "helpcog", "staff", "ide"):
                continue
            cog: Cog = _bot.get_cog(cog_name)
            if getattr(cog, "ignore", None):
                continue
            embed.add_field(
                name=f"{cog.emoji} {cog.qualified_name.upper()} COMMANDS [{len(cog.get_commands())}]",  # type: ignore
                value=f"➥ {cog.short_help_doc}",  # type: ignore
                inline=False,
            )
        embed.set_author(
            name=f"{_bot.user.name.upper()} HELP", icon_url=_bot.user.display_avatar.url
        )
        embed.set_footer(
            text=f"Requested by {self.context.author}",
            icon_url=self.context.author.display_avatar.url,
        )
        embed.set_thumbnail(url=_bot.user.display_avatar.url)
        view = HelpView()
        view.add_item(NavigatorMenu(self.context))
        view.message = await self.context.reply(
            embed=embed, mention_author=False, view=view
        )

    async def send_command_help(self, cmd: Command):
        """
        Called upon a command arg being supplied ;
        Read , needs to be polished
        """
        command_help_dict = {
            "aliases": " , ".join(cmd.aliases) or "No aliases",
            "description": cmd.description or cmd.brief or "No description Provided",
        }
        command_signature = ""
        for arg in cmd.signature.split("] ["):
            if "=" in arg:
                parsed_arg = "{" + arg.split("=")[0].strip("[]<>]") + "}"
            else:
                parsed_arg = "[" + arg.strip("[]<>") + "]"
                if parsed_arg == "[]":
                    parsed_arg = ""
            command_signature += parsed_arg + " "
        usage = f"```ini\n{await self.context.bot.get_prefix(self.context.message)} {cmd.name} {command_signature}\n```"
        embed = Embed(
            color=Color.og_blurple(),
            description="\n".join(
                f"`{key}` **:** {command_help_dict[key]}"
                for key in command_help_dict.keys()
            ),
        )
        embed.set_author(
            name=f"{cmd.name.upper()} COMMAND",
            icon_url=self.context.bot.user.display_avatar.url,
        )
        embed.add_field(name="USAGE", value=usage)
        embed.set_footer(text="[] : Required | {} : Optional")
        await self.context.reply(embed=embed, mention_author=False)

    async def send_group_help(self, group: Group):
        """
        Group Commands , would rarely be used
        """
        desc = "\n".join(
            f"`{cmd.name}` **:** {cmd.short_doc or 'No help text'}"
            for cmd in group.commands
        )
        embed = Embed(
            description=group.description
            or f"{group.qualified_name.title()} Group" + desc,
            color=Color.og_blurple(),
        )
        await self.context.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog: Cog):
        """
        Help for a specific cog , gets embed through `embed_from_cog` fn , which is used for both manual and drop menu cog help
        """
        embed = await embed_for_cog(cog, self.context)
        await self.context.reply(embed=embed, mention_author=False)


class HelpView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.message = None

    async def on_timeout(self) -> None:
        item = self.children[0]
        item.disabled = True
        await self.message.edit(view=self)


class NavigatorMenu(Select):
    def __init__(self, ctx: Context) -> None:
        self.context: Context = ctx
        options = []
        for cog_name in ctx.bot.cogs:
            if cog_name.lower() in ("jishaku", "helpcog", "staff", "ide"):
                continue
            cog: Cog = ctx.bot.get_cog(cog_name)
            if getattr(cog, "ignore", None):
                continue
            options.append(
                SelectOption(
                    label=f"{cog.qualified_name.upper()} COMMANDS",
                    description=cog.description.replace("cog", "module"),
                    emoji=cog.emoji,  # type: ignore
                )
            )
        super().__init__(placeholder="Navigate to Category", options=options)

    async def callback(self, interaction: MessageInteraction):
        cog_s = [
            self.context.bot.get_cog(cog)
            for cog in self.context.bot.cogs
            if interaction.values[0].lower().replace(" commands", "")
            == self.context.bot.get_cog(cog).qualified_name.lower()
        ]
        embed = await embed_for_cog(cog_s[0], self.context)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed)


async def embed_for_cog(cog: Cog, ctx: Context):
    desc = "\n".join(
        f"`{cmd.name}` **:** {cmd.short_doc or 'No help text'}"
        for cmd in cog.get_commands()
    )
    embed = (
        Embed(
            color=Color.og_blurple(),
            description="Use `jarvide help <command>` for more info about commands\n\n"
            + desc,
        )
        .set_author(
            name=f"{cog.qualified_name.upper()} CATEGORY",
            icon_url=ctx.bot.user.display_avatar.url,
        )
        .set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
        )
    )
    return embed
