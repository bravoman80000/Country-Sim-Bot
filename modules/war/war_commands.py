import discord
from discord import app_commands
from discord.ext import commands

from war_utils import load_wars, save_wars
from config import GM_ROLE_NAME
from utils import interpret_roll, normalize_name
from checks import is_gm_check
import datetime
import random
from typing import Optional, Literal

# === /declarewar Command ===


@is_gm_check()
@app_commands.describe(
    name="The title of the war",
    attacker="Who is declaring the war?",
    defender="Who is being attacked?",
    intensity="How intense is the war? (1–10)",
    attacker_emoji="Emoji for the attacker (defaults to 🟥)",
    defender_emoji="Emoji for the defender (defaults to 🟦)",
)
async def declarewar(
    interaction: discord.Interaction,
    name: str,
    attacker: str,
    defender: str,
    intensity: int = 5,
    attacker_emoji: str = "\U0001f7e5",
    defender_emoji: str = "\U0001f7e6",
):

    wars = load_wars()
    new_war = {
        "name": name,
        "attacker": attacker,
        "defender": defender,
        "momentum": 0,
        "intensity": intensity,
        "attacker_emoji": attacker_emoji,
        "defender_emoji": defender_emoji,
        "status": "active",
        "started_at": str(datetime.date.today()),
    }
    wars["wars"].append(new_war)
    save_wars(wars)

    await interaction.response.send_message(
        f"👮 **The Archivist records a new war...**\n"
        f"{attacker_emoji} {attacker} vs {defender} {defender_emoji}\n"
        f"📖 Title: *{name}*\n"
        f"🔥 Intensity: {intensity} (War Bar size)\n"
        f"🗖️ Begun: {new_war['started_at']}\n"
        f"📊 Momentum set to ⚔️ (0)"
    )


declarewar_cmd = app_commands.Command(
    name="declarewar",
    description="Declare a new war between two nations.",
    callback=declarewar,
)

# === /resolvebattle Command ===


@is_gm_check()
@app_commands.describe(
    war="(Optional) The war this battle belongs to",
    attacker="Attacking faction",
    defender="Defending faction",
    modifier="Modifier (-3 to +3)",
    roll_mode="Roll mode: Advantage, Disadvantage, or None",
)
async def resolvebattle(
    interaction: discord.Interaction,
    war: Optional[str],
    attacker: str,
    defender: str,
    modifier: int = 0,
    roll_mode: Optional[Literal["Advantage", "Disadvantage", "None"]] = "None",
):
    roll_1 = random.randint(1, 10)
    roll_2 = random.randint(1, 10)

    if roll_mode == "Advantage":
        base_roll = max(roll_1, roll_2)
        roll_explanation = f"🎲 Rolls: {roll_1}, {roll_2} → Chose higher"
    elif roll_mode == "Disadvantage":
        base_roll = min(roll_1, roll_2)
        roll_explanation = f"🎲 Rolls: {roll_1}, {roll_2} → Chose lower"
    else:
        base_roll = roll_1
        roll_explanation = f"🎲 Roll: {roll_1}"

    final_roll = max(1, min(10, base_roll + modifier))
    outcome = interpret_roll(final_roll)
    war_title = war.replace("_", " ").title() if war else "Independent Engagement"

    await interaction.response.send_message(
        f"📜 *The Archivist opens the ledger...*\n\n"
        f"⚔️ **{war_title}**\n"
        f"🎯 Attacker: **{attacker.title()}**\n"
        f"🛡️ Defender: **{defender.title()}**\n\n"
        f"{roll_explanation}\n"
        f"🔧 Modifier: {modifier}\n"
        f"📟 Final Roll: **{final_roll}**\n\n"
        f"📖 **Outcome:** {outcome}"
    )


resolvebattle_cmd = app_commands.Command(
    name="resolvebattle",
    description="Resolve a battle between two factions.",
    callback=resolvebattle,
)

# === /updatewar Command ===


@is_gm_check()
@app_commands.describe(
    name="Name of the war", change="Momentum adjustment (positive or negative)"
)
async def updatewar(interaction: discord.Interaction, name: str, change: int):
    wars = load_wars()
    for war in wars["wars"]:
        if war["name"].lower() == name.lower() and war["status"] == "active":
            war["momentum"] += change
            save_wars(wars)
            await interaction.response.send_message(
                f"⚖️ Updated **{war['name']}** momentum to {war['momentum']}."
            )
            return
    await interaction.response.send_message(
        "❌ No active war by that name found.", ephemeral=True
    )


updatewar_cmd = app_commands.Command(
    name="updatewar",
    description="Update the momentum value of a war",
    callback=updatewar,
)

# === /editwar Command ===


@is_gm_check()
@app_commands.describe(
    name="Name of the war to edit",
    new_attacker="(Optional) New attacker name",
    new_defender="(Optional) New defender name",
    new_intensity="(Optional) New war intensity (1–20)",
    new_attacker_emoji="(Optional) New emoji for the attacker",
    new_defender_emoji="(Optional) New emoji for the defender",
)
async def editwar(
    interaction: discord.Interaction,
    name: str,
    new_attacker: Optional[str] = None,
    new_defender: Optional[str] = None,
    new_intensity: Optional[int] = None,
    new_attacker_emoji: Optional[str] = None,
    new_defender_emoji: Optional[str] = None,
):
    wars = load_wars()
    for war in wars["wars"]:
        if war["name"].lower() == name.lower() and war["status"] == "active":
            if new_attacker:
                war["attacker"] = new_attacker
            if new_defender:
                war["defender"] = new_defender
            if new_intensity:
                war["intensity"] = max(1, min(20, new_intensity))
            if new_attacker_emoji:
                war["attacker_emoji"] = new_attacker_emoji
            if new_defender_emoji:
                war["defender_emoji"] = new_defender_emoji
            save_wars(wars)
            await interaction.response.send_message(
                f"✏️ Updated **{war['name']}**.\n"
                f"Now {war['attacker_emoji']} **{war['attacker']}** vs {war['defender']} {war['defender_emoji']} | Intensity: {war['intensity']}"
            )
            return
    await interaction.response.send_message(
        "❌ War not found or inactive.", ephemeral=True
    )


editwar_cmd = app_commands.Command(
    name="editwar",
    description="[GM] Edit war details like attacker, defender, emojis, or intensity.",
    callback=editwar,
)

# === Autocompletes ===


@resolvebattle_cmd.autocomplete("attacker")
async def attacker_autocomplete(interaction: discord.Interaction, current: str):
    wars = load_wars()
    war_name = getattr(interaction.namespace, "war", None)

    if war_name:
        war = next(
            (
                w
                for w in wars["wars"]
                if w["name"].lower() == war_name.lower() and w["status"] == "active"
            ),
            None,
        )
        if war:
            return [
                app_commands.Choice(name=war["attacker"], value=war["attacker"]),
                app_commands.Choice(name=war["defender"], value=war["defender"]),
            ]
    return []


@resolvebattle_cmd.autocomplete("defender")
async def defender_autocomplete(interaction: discord.Interaction, current: str):
    return await attacker_autocomplete(interaction, current)


@resolvebattle_cmd.autocomplete("war")
@updatewar_cmd.autocomplete("name")
@editwar_cmd.autocomplete("name")
async def war_autocomplete(interaction: discord.Interaction, current: str):
    wars = load_wars()
    return [
        app_commands.Choice(name=w["name"], value=w["name"])
        for w in wars["wars"]
        if w["status"] == "active" and current.lower() in w["name"].lower()
    ][:25]


# === Setup Function ===


def setup(bot: commands.Bot):
    bot.tree.add_command(declarewar_cmd)
    bot.tree.add_command(resolvebattle_cmd)
    bot.tree.add_command(updatewar_cmd)
    bot.tree.add_command(editwar_cmd)
