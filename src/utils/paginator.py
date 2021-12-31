from typing import Union

from disnake import MessageInteraction, ApplicationCommandInteraction, Embed, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class TextPaginator(View):
    """A paginator, used to paginate long texts.

    Parameters
    ----------
        ctx: :class:`.Context`
            The context object to use for this paginator.

        text: :class:`str`
            The text to paginate.

        breakpoint: :class:`int`
            The breakpoint where it cuts the text and puts the rest on the next page. Defaults to 2000.

        prefix: :class:`str`
            The prefix that appears at the start of every page.

        suffix: :class:`str`
            The suffix that appears at the end of every page.

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
        breakpoint: int = 2000,
        prefix: str = '',
        suffix: str = '',
        timeout: float = 180.0
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.text = text
        self.breakpoint = breakpoint
        self.prefix = prefix
        self.suffix = suffix

        self.current_page = 0
        self.pages = []

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

    def _get_pages(self):
        text = self.text
        while True:
            if len(text) != 0:
                new_text = text[0:self.breakpoint]
                if self.prefix:
                    new_text = self.prefix + '\n' + new_text
                if self.suffix:
                    new_text = new_text + '\n' + self.suffix
                text = text[self.breakpoint:]
                self.pages.append(new_text)
            else:
                break

    async def _show_page(self, page_number: int) -> None:
        if page_number < 0:
            return
        elif page_number >= len(self.pages):
            return

        self.current_page = page_number
        em = Embed(description=self.pages[self.current_page])
        em.set_footer(text=f'Page {self.current_page + 1}/{len(self.pages)}')

        self._update_labels()
        await self.message.edit(embed=em, view=self)

    async def start(self):
        self._get_pages()
        em = Embed(description=self.pages[self.current_page])
        em.set_footer(text=f'Page {self.current_page + 1}/{len(self.pages)}')

        self._update_labels()
        self.message = await self.ctx.send(embed=em, view=self)

    async def interaction_check(self, inter: MessageInteraction) -> bool:
        owners = self.ctx.bot.owner_ids or self.ctx.bot.owner_id if self.ctx.bot else 0
        if inter.author.id not in (self.ctx.author.id, owners):
            await inter.send(
                'You cannot use the buttons on this paginator because you '
                'are not the one who invoked the command!',
                ephemeral=True
            )
            return False
        return True

    @button(label='≪')
    async def first_page(self, button: Button, inter: MessageInteraction):
        """Goes to the first page."""
        await inter.response.defer()
        await self._show_page(0)

    @button(label='Back', style=ButtonStyle.blurple)
    async def previous_page(self, button: Button, inter: MessageInteraction):
        """Goes to the previous page."""
        await inter.response.defer()
        await self._show_page(self.current_page - 1)

    @button(label='Next', style=ButtonStyle.blurple)
    async def next_page(self, button: Button, inter: MessageInteraction):
        """Goes to the next page."""
        await inter.response.defer()
        await self._show_page(self.current_page + 1)

    @button(label='≫')
    async def last_page(self, button: Button, inter: MessageInteraction):
        """Goes to the last page."""
        await inter.response.defer()
        await self._show_page(len(self.pages) - 1)

    @button(label='Exit', style=ButtonStyle.red)
    async def exit(self, button: Button, inter: MessageInteraction):
        """Exits the paginator by deleting the paginator message."""
        await inter.response.defer()
        await self.message.delete()
        self.stop()
