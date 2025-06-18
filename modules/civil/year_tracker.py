import discord
from discord.ext import commands
from discord import app_commands
import os
import json

TRACKER_PATH = "/data/turn_tracker.json"

def load_tracker():
    if not os.path.exists(TRACKER_PATH):
        return {"year": 1444, "turn": 1}
    with open(TRACKER_PATH, "r") as f:
        return json.load(f)

def save_tracker(data):
    with open(TRACKER_PATH, "w") as f:
        json.dump(data, f, indent=4)


class YearTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="startturn", description="Advance to the next turn (increments turn/year).")
    async def start_turn(self, interaction: discord.Interaction):
        tracker = load_tracker()
        tracker["turn"] += 1
        if tracker["turn"] > 4:
            tracker["turn"] = 1
            tracker["year"] += 1
        save_tracker(tracker)

        await interaction.response.send_message(
            f"📅 It is now Turn {tracker['turn']} of the year {tracker['year']}.",
            ephemeral=False
        )

    @app_commands.command(name="checkturn", description="Check the current turn and year.")
    async def check_turn(self, interaction: discord.Interaction):
        tracker = load_tracker()
        await interaction.response.send_message(
            f"📖 The Archivist whispers: It is Turn {tracker['turn']} of the year {tracker['year']}.",
            ephemeral=True
        )

@app_commands.command(name="setturn", description="📜 GM: Set the current year and turn manually.")
@app_commands.describe(
    year="The year to set (e.g., 1446)",
    turn="The turn to set (1–4)"
)
async def set_turn(self, interaction: discord.Interaction, year: int, turn: int):
    # Fetch the full member object
    member = await interaction.guild.fetch_member(interaction.user.id)

    if not any(role.name == "GM (Game Managers)" for role in member.roles):
        await interaction.response.send_message("❌ Only GMs may alter the fabric of time.", ephemeral=True)
        return

    if turn < 1 or turn > 4:
        await interaction.response.send_message("⚠️ Turn must be between 1 and 4.", ephemeral=True)
        return

    tracker = {"year": year, "turn": turn}
    save_tracker(tracker)

    await interaction.response.send_message(
        f"📝 Time has been rewritten. It is now Turn {turn} of the year {year}.",
        ephemeral=False
    )



async def setup(bot):
    await bot.add_cog(YearTracker(bot))
