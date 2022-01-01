import disnake
from disnake.ext import commands

from typing import Optional


class ConfirmationView(disnake.ui.View):
    def __init__(self, *, timeout: float, author_id: int) -> None:
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.author_id = author_id

    async def on_timeout(self) -> None:
        await self.message.delete()

    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True

        await interaction.response.send_message(
            "This confirmation dialog is not for you.", ephemeral=True
        )
        return False

    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green)
    async def confirm(
        self, button: disnake.ui.Button, interaction: disnake.Interaction
    ):
        self.value = True
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.value = False
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()


async def prompt(ctx: commands.Context, *, message: str, timeout: float):
    """An interactive reaction confirmation dialog

    Parameters
    -----------
    ctx: `disnake.ext.commands.Context`
        The context in which this prompt was invoked in.
    message: `str`
        The message to show along with the prompt.
    timeout: `float`
        The time in seconds before this function returns `None`

    Returns
    --------
    Optional[bool]
        ``True`` if explicit confirm,

        ``False`` if explicit deny,

        ``None`` if deny due to timeout
    """

    view = ConfirmationView(timeout=timeout, author_id=ctx.author.id)
    view.message = await ctx.send(message, view=view)
    await view.wait()
    return view.value
