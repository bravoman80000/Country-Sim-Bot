import discord
from discord import app_commands
from discord.ext import commands

from modules.war.war_utils import load_wars, save_wars
from config import GM_ROLE_NAME
from checks import is_gm_check

# === /warledger Command ===


@app_commands.describe(show_closed="Include closed wars in the list?")
async def warledger(interaction: discord.Interaction, show_closed: bool = False):
    wars = load_wars()
    visible = [w for w in wars["wars"] if show_closed or w["status"] == "active"]

    if not visible:
        await interaction.response.send_message(
            "📖 No wars found in the Archivist's records."
        )
        return

    message = "📚 **The Archivist's War Ledger:**\n"
    for war in visible:
        status = "✅ Closed" if war["status"] == "closed" else "🔥 Active"
        end = war.get("ended_at", "Ongoing")
        message += (
            f"\n• **{war['name']}** ({status})\n"
            f"  {war['attacker']} vs {war['defender']}\n"
            f"  Intensity: {war['intensity']} | Dates: {war['started_at']} - {end}\n"
        )

    await interaction.response.send_message(message)


warledger_cmd = app_commands.Command(
    name="warledger",
    description="View a list of all current or past wars",
    callback=warledger,
)

# === /deletewar Command ===


@is_gm_check()
@app_commands.describe(war_name="The name of the war to permanently delete")
async def deletewar(interaction: discord.Interaction, war_name: str):
    wars = load_wars()
    war_name_cleaned = war_name.strip().lower()
    before = len(wars["wars"])
    wars["wars"] = [w for w in wars["wars"] if w["name"].lower() != war_name_cleaned]
    after = len(wars["wars"])

    if before == after:
        await interaction.response.send_message(
            "⚠️ No war by that name found to delete.", ephemeral=True
        )
    else:
        save_wars(wars)
        await interaction.response.send_message(
            f"🗑️ War **{war_name}** has been permanently removed from the records."
        )


deletewar_cmd = app_commands.Command(
    name="deletewar",
    description="[GM] Remove a war permanently from the ledger",
    callback=deletewar,
)


@deletewar_cmd.autocomplete("war_name")
async def deletewar_autocomplete(interaction: discord.Interaction, current: str):
    wars = load_wars()
    return [
        app_commands.Choice(name=w["name"], value=w["name"])
        for w in wars["wars"]
        if current.lower() in w["name"].lower()
    ][:25]


# === Setup ===


def setup(bot: commands.Bot):
    bot.tree.add_command(warledger_cmd)
    bot.tree.add_command(deletewar_cmd)
