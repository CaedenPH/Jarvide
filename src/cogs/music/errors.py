import disnake
from typing import Optional
from disnake.ext import commands

class NoChannelProvided(commands.CommandError):
    """Raised when no suitable voice channel is provided """
    def __init__(self, botmessage: Optional[disnake.Message] = None)-> None:
        self.botmessage = botmessage

class IncorrectChannelError(commands.CommandError):
    """Raised when commands are used outside of the player's channel"""
    pass