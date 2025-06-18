import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
import os
import json
import random

DATA_PATH = "/data/countries.json"

# Ensure the data file exists
def load_countries():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_countries(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Tier value ranges
ECONOMY_TIERS = {
    "Collapsed": (1, 24),
    "Subsistence": (25, 74),
    "Scraping By": (75, 149),
    "Growing": (150, 224),
    "Developing": (225, 299),
    "Established": (300, 374),
    "Thriving": (375, 449),
    "Commercialized": (450, 549),
    "Prosperous": (550, 649),
    "Powerhouse": (650, 774),
    "Great Power": (775, 899),
    "Juggernaut": (900, 999),
    "Hegemon": (1000, 1499),
    "World Engine": (1500, 1999),
    "Economic Singularity": (2000, 3000),
}

STABILITY_TIERS = {
    "Anarchy": (0, 9),
    "Uprising": (10, 19),
    "Chaotic": (20, 34),
    "Unstable": (35, 49),
    "Shaky": (50, 59),
    "Stable": (60, 69),
    "Cohesive": (70, 79),
    "Harmonized": (80, 89),
    "Unified": (90, 97),
    "Iron Order": (98, 100),
}

MILITARY_TIERS = {
    "Trivial": (1, 9),
    "Light": (10, 24),
    "Moderate": (25, 49),
    "Heavy": (50, 74),
    "Overwhelming": (75, 100),
}

class CountryRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="registercountry", description="Register a new country in the Archivist's ledger.")
    @app_commands.describe(
        name="Name of the country",
        leader="Title or name of its current ruler",
        military_tier="Select the military tier",
        stability_tier="Select the stability tier",
        economy_tier="Select the economic tier",
        morale="Morale condition (Low, Normal, High, Unbreakable)",
        supply="Supply level (Starving, Low, Adequate, Abundant)",
        composition="Optional unit composition summary",
        tags="Optional tags like Reformist, Isolationist, Elite (comma-separated)"
    )
    @app_commands.choices(
        military_tier=[app_commands.Choice(name=k, value=k) for k in MILITARY_TIERS],
        stability_tier=[app_commands.Choice(name=k, value=k) for k in STABILITY_TIERS],
        economy_tier=[app_commands.Choice(name=k, value=k) for k in ECONOMY_TIERS],
        morale=[
            app_commands.Choice(name="Low", value="Low"),
            app_commands.Choice(name="Normal", value="Normal"),
            app_commands.Choice(name="High", value="High"),
            app_commands.Choice(name="Unbreakable", value="Unbreakable"),
        ],
        supply=[
            app_commands.Choice(name="Starving", value="Starving"),
            app_commands.Choice(name="Low", value="Low"),
            app_commands.Choice(name="Adequate", value="Adequate"),
            app_commands.Choice(name="Abundant", value="Abundant"),
        ]
    )
    async def register_country(
        self,
        interaction: discord.Interaction,
        name: str,
        leader: str,
        military_tier: app_commands.Choice[str],
        stability_tier: app_commands.Choice[str],
        economy_tier: app_commands.Choice[str],
        morale: app_commands.Choice[str],
        supply: app_commands.Choice[str],
        composition: str = "",
        tags: str = ""
    ):
        countries = load_countries()

        if name in countries:
            await interaction.response.send_message(
                f"⚠️ The Archivist has already recorded **{name}**.", ephemeral=True)
            return

        # Roll stats
        econ_val = random.randint(*ECONOMY_TIERS[economy_tier.value])
        stab_val = random.randint(*STABILITY_TIERS[stability_tier.value])
        mil_val = random.randint(*MILITARY_TIERS[military_tier.value])

        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

        countries[name] = {
            "leader": leader,
            "military_strength": {
                "tier": military_tier.value,
                "value": mil_val
            },
            "stability": {
                "tier": stability_tier.value,
                "value": stab_val
            },
            "economy": {
                "tier": economy_tier.value,
                "value": econ_val
            },
            "morale": morale.value,
            "supply": supply.value,
            "composition": composition,
            "tags": tag_list
        }

        save_countries(countries)

        embed = discord.Embed(
            title=f"📜 The Archivist Records {name}",
            description=(
                f"*The Archivist strikes pen to paper, recording the histories of these people...*\n\n"
                f"**Ruler:** {leader}\n"
                f"🛡 **Military:** {military_tier.value}\n"
                f"💰 **Economy:** {economy_tier.value}\n"
                f"🏛 **Stability:** {stability_tier.value}\n"
                f"🧠 **Morale:** {morale.value} | 📦 **Supply:** {supply.value}\n"
            ),
            color=discord.Color.gold()
        )

        if composition:
            embed.add_field(name="🪖 Unit Composition", value=composition, inline=False)
        if tag_list:
            embed.add_field(name="🏷 Tags", value=", ".join(tag_list), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(CountryRegister(bot))
