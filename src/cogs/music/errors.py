from disnake.ext import commands

class NoChannelProvided(commands.CommandError):
    """Raised when no suitable voice channel is provided """
    pass

class IncorrectChannelError(commands.CommandError):
    """Raised when commands are used outside of the player's channel"""
    pass