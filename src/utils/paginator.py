from typing import Union
from abc import abstractmethod, ABC

from disnake import (
    MessageInteraction,
    ApplicationCommandInteraction,
    Embed,
    ButtonStyle,
    Message,
)
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class LineTooLong(Exception):
    ...


class PageTooLong(Exception):
    ...


class _AbstractPaginator(View, ABC):
    """The abstract class that every paginator should inherit from.
    In order to use this paginator, you need to subclass this object and override the `get_pages` method
    with your own that adds pages to ``self.pages``.

    NOTE: Never ``.start`` the paginator if you haven't subclassed it and overridden the `get_pages` method.

    Parameters
    ----------
        ctx: Union[:class:`.Context`, :class:`.MessageInteraction`, :class:`.ApplicationCommandInteraction`]
            The context/interaction object to use for this paginator.

        message: :class:`.Message`
            The message object to use instead of sending another message.

        embed_footer_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_footer`` embed method.

        embed_author_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_author`` embed method.

        timeout: :class:`float`
            The time for how long the paginator is supposed to wait for an interaction until it times out.

    Methods
    -------
        `start`
            |coro|

            Starts the paginator.
    """

    def __init__(
        self,
        ctx: Union[Context, MessageInteraction, ApplicationCommandInteraction],
        *,
        message: Message = None,
        embed_footer_kwargs: dict[str, str] = None,
        embed_author_kwargs: dict[str, str] = None,
        timeout: float = 180.0,
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.message = message
        self.embed_footer_kwargs = embed_footer_kwargs
        self.embed_author_kwargs = embed_author_kwargs

        self.current_page = 0
        self.pages = []

    @abstractmethod
    def get_pages(self):
        pass

    def _update_labels(self):
        if len(self.pages) == 1:
            self.clear_items()
            self.add_item(self.exit)
            return

        if self.current_page == 0:
            self.first_page.disabled = self.previous_page.disabled = True
        else:
            self.first_page.disabled = self.previous_page.disabled = False

        if self.current_page == len(self.pages) - 1:
            self.last_page.disabled = self.next_page.disabled = True
        else:
            self.last_page.disabled = self.next_page.disabled = False

    async def _show_page(self, page_number: int) -> None:
        if page_number < 0:
            return
        elif page_number >= len(self.pages):
            return

        self.current_page = page_number
        em = Embed(description=self.pages[self.current_page])

        page_footer = f"Page {self.current_page + 1}/{len(self.pages)}"
        footer_kwargs = {"text": page_footer}
        if self.embed_footer_kwargs:
            footer_text = self.embed_footer_kwargs.get("text")
            icon_url = self.embed_footer_kwargs.get("icon_url")
            if footer_text is not None:
                page_footer = footer_text + " • " + page_footer
                footer_kwargs["text"] = page_footer
            if icon_url is not None:
                footer_kwargs["icon_url"] = icon_url
        em.set_footer(**footer_kwargs)

        if self.embed_author_kwargs:
            em.set_author(**self.embed_author_kwargs)
        self._update_labels()
        await self.message.edit(embed=em, view=self)

    async def start(self):
        self.get_pages()
        em = Embed(description=self.pages[self.current_page])
        page_footer = f"Page {self.current_page + 1}/{len(self.pages)}"
        footer_kwargs = {"text": page_footer}
        if self.embed_footer_kwargs:
            footer_text = self.embed_footer_kwargs.get("text")
            icon_url = self.embed_footer_kwargs.get("icon_url")
            if footer_text is not None:
                page_footer = footer_text + " • " + page_footer
                footer_kwargs["text"] = page_footer
            if icon_url is not None:
                footer_kwargs["icon_url"] = icon_url
        em.set_footer(**footer_kwargs)

        if self.embed_author_kwargs:
            em.set_author(**self.embed_author_kwargs)

        self._update_labels()
        if self.message is None:
            self.message = await self.ctx.channel.send(embed=em, view=self)
        else:
            await self.message.edit(embed=em, view=self)

    async def interaction_check(self, inter: MessageInteraction) -> bool:
        owners = self.ctx.bot.owner_ids or self.ctx.bot.owner_id if self.ctx.bot else 0
        if inter.author.id not in (self.ctx.author.id, owners):
            await inter.send(
                "You cannot use the buttons on this paginator because you "
                "are not the one who invoked the command!",
                ephemeral=True,
            )
            return False
        return True

    @button(label="Start")
    async def first_page(self, button: Button, inter: MessageInteraction):
        """Goes to the first page."""
        await inter.response.defer()
        await self._show_page(0)

    @button(label="Prev", style=ButtonStyle.blurple)
    async def previous_page(self, button: Button, inter: MessageInteraction):
        """Goes to the previous page."""
        await inter.response.defer()
        await self._show_page(self.current_page - 1)

    @button(label="Next", style=ButtonStyle.blurple)
    async def next_page(self, button: Button, inter: MessageInteraction):
        """Goes to the next page."""
        await inter.response.defer()
        await self._show_page(self.current_page + 1)

    @button(label="End")
    async def last_page(self, button: Button, inter: MessageInteraction):
        """Goes to the last page."""
        await inter.response.defer()
        await self._show_page(len(self.pages) - 1)

    @button(label="Exit", style=ButtonStyle.red)
    async def exit(self, button: Button, inter: MessageInteraction):
        """Exits the paginator by deleting the paginator message."""
        await inter.response.defer()
        await self.message.delete()
        self.stop()


class TextPaginator(_AbstractPaginator):
    """A paginator, used to paginate long texts.

    Parameters
    ----------
        ctx: Union[:class:`.Context`, :class:`.MessageInteraction`, :class:`.ApplicationCommandInteraction`]
            The context/interaction object to use for this paginator.

        text: :class:`str`
            The text to paginate.

        break_point: :class:`int`
            The breakpoint where it cuts the text and puts the rest on the next page. Defaults to 2000.

        prefix: :class:`str`
            The prefix that appears at the start of every page.

        suffix: :class:`str`
            The suffix that appears at the end of every page.

        message: :class:`.Message`
            The message object to use instead of sending another message.

        embed_footer_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_footer`` embed method.

        embed_author_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_author`` embed method.

        timeout: :class:`float`
            The time for how long the paginator is supposed to wait for an interaction until it times out.

    Methods
    -------
        `start`
            |coro|

            Starts the paginator.
    """

    def __init__(
        self,
        ctx: Union[Context, MessageInteraction, ApplicationCommandInteraction],
        text: str,
        *,
        break_point: int = 2000,
        prefix: str = "",
        suffix: str = "",
        message: Message = None,
        embed_footer_kwargs: dict[str, str] = None,
        embed_author_kwargs: dict[str, str] = None,
        timeout: float = 180.0,
    ):
        super().__init__(
            ctx=ctx,
            timeout=timeout,
            message=message,
            embed_footer_kwargs=embed_footer_kwargs,
            embed_author_kwargs=embed_author_kwargs,
        )
        self.text = text
        self.breakpoint = break_point
        self.prefix = prefix
        self.suffix = suffix

    def get_pages(self):
        text = self.text
        while True:
            if len(text) != 0:
                new_text = text[0 : self.breakpoint]
                if self.prefix:
                    new_text = self.prefix + "\n" + new_text
                if self.suffix:
                    new_text = new_text + "\n" + self.suffix
                text = text[self.breakpoint :]
                self.pages.append(new_text)
            else:
                break


class LinePaginator(_AbstractPaginator):
    """A paginator, used to paginate over a list of lines.

    Parameters
    ----------
        ctx: Union[:class:`.Context`, :class:`.MessageInteraction`, :class:`.ApplicationCommandInteraction`]
            The context/interaction object to use for this paginator.

        lines: :class:`list`
            The list of lines to paginate over.

        line_limit: :class:`int`
            The limit of how many lines should be displayed per page. Defaults to 10.

        prefix: :class:`str`
            The prefix that appears at the start of every page.

        suffix: :class:`str`
            The suffix that appears at the end of every page.

        message: :class:`.Message`
            The message object to use instead of sending another message.

        embed_footer_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_footer`` embed method.

        embed_author_kwargs: :class:`dict`
            A dict containing the kwargs for the ``.set_author`` embed method.

        timeout: :class:`float`
            The time for how long the paginator is supposed to wait for an interaction until it times out.

    Methods
    -------
        `start`
            |coro|

            Starts the paginator.
    """

    def __init__(
        self,
        ctx: Union[Context, MessageInteraction, ApplicationCommandInteraction],
        lines: list[str],
        *,
        line_limit: int = 10,
        prefix: str = "",
        suffix: str = "",
        message: Message = None,
        embed_footer_kwargs: dict[str, str] = None,
        embed_author_kwargs: dict[str, str] = None,
        timeout: float = 180.0,
    ):
        super().__init__(
            ctx=ctx,
            timeout=timeout,
            message=message,
            embed_footer_kwargs=embed_footer_kwargs,
            embed_author_kwargs=embed_author_kwargs,
        )
        self.lines = lines
        self.line_limit = line_limit
        self.prefix = prefix
        self.suffix = suffix

    def _lines_to_page(self, lines: list[str]):
        page = "".join(lines)
        if self.prefix:
            page = self.prefix + "\n" + page
        if self.suffix:
            page = page + "\n" + self.suffix

        return page

    def get_pages(self):
        lines = []
        line_index = 0
        page_index = 0
        for line in self.lines:
            if len(line) > 4096:
                raise LineTooLong(
                    f"Expected the line at index {line_index} to be less than 4096 characters"
                )

            lines.append(line)
            if len(lines) >= self.line_limit:
                page = self._lines_to_page(lines)
                if len(page) > 4096:
                    raise PageTooLong(
                        f"Page at index {page_index} has to be less than 4096 characters. "
                        "Please lessen the 'line_limit'"
                    )
                page_index += 1
                self.pages.append(page)
                lines = []
            line_index += 1
        else:
            if lines:
                page = self._lines_to_page(lines)
                if len(page) > 4096:
                    raise PageTooLong(
                        f"Page at index {page_index} has to be less than 4096 characters. "
                        "Please lessen the 'line_limit'"
                    )
                self.pages.append(page)
