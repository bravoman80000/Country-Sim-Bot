# checks.py

from discord import Interaction
from discord.app_commands import check
from config import GM_ROLE_NAME


def is_gm_check():

    async def predicate(interaction: Interaction):
        return any(role.name == GM_ROLE_NAME
                   for role in interaction.user.roles)

    return check(predicate)
