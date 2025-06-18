import discord
from discord import app_commands
from discord.ext import commands

from modules.war.war_utils import load_wars
from utils import normalize_name


# === /warbar Command ===
async def warbar(interaction: discord.Interaction, war_name: str):
    wars = load_wars()
    war_name_cleaned = normalize_name(war_name)
    war = next(
        (
            w
            for w in wars["wars"]
            if normalize_name(w["name"]) == war_name_cleaned and w["status"] == "active"
        ),
        None,
    )

    if not war:
        await interaction.response.send_message(
            "❌ No active war found.", ephemeral=True
        )
        return

    intensity = war.get("intensity", 5)
    momentum = max(-intensity, min(intensity, war.get("momentum", 0)))
    total_slots = intensity * 2 + 1
    half = total_slots // 2

    attacker_tiles = war["attacker_emoji"] * (half + momentum)
    defender_tiles = war["defender_emoji"] * (half - momentum)
    bar = f"{attacker_tiles}⚔️{defender_tiles}"

    await interaction.response.send_message(
        f"📊 **{war['name'].title()}**\n"
        f"{war['attacker']} vs {war['defender']}\n\n"
        f"{bar}\n\n"
        f"📆 Intensity: {intensity} | 📈 Momentum: {momentum:+}"
    )


# Define the command object after the function
warbar_cmd = app_commands.Command(
    name="warbar",
    description="View the current war bar for a war.",
    callback=warbar,
)


# Autocomplete for warbar
@warbar_cmd.autocomplete("war_name")
async def warbar_autocomplete(interaction: discord.Interaction, current: str):
    wars = load_wars()
    return [
        app_commands.Choice(name=w["name"], value=w["name"])
        for w in wars["wars"]
        if w["status"] == "active" and current.lower() in w["name"].lower()
    ][:25]


# Setup function
def setup(bot: commands.Bot):
    bot.tree.add_command(warbar_cmd)
