import discord  # type: ignore
from discord import app_commands  # type: ignore
from discord.ext import commands  # type: ignore
import os
import json

DATA_PATH = os.path.join("data", "countries.json")

# === Load Country Data ===
def load_countries():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

# === Autocomplete Helper ===
async def autocomplete_country_names(interaction: discord.Interaction, current: str):
    data = load_countries()
    return [
        app_commands.Choice(name=name, value=name)
        for name in data
        if current.lower() in name.lower()
    ][:25]


# === Tiers for Reference ===
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
    "Revolution": (1, 24),
    "Instability": (25, 74),
    "Tenuous": (75, 149),
    "Stable": (150, 224),
    "Peaceful": (225, 299),
    "Golden Age": (300, 375),
}

MORALE_TIERS = {
    "Low": (1, 33),
    "Normal": (34, 66),
    "High": (67, 89),
    "Unbreakable": (90, 100),
}

SUPPLY_TIERS = {
    "Starving": (1, 24),
    "Low": (25, 49),
    "Adequate": (50, 74),
    "Abundant": (75, 100),
}

class CountryQueries(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === Check Economy Command ===
    @app_commands.command(name="checkeco", description="Check a country's economic tier.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checkeco(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ The Archivist finds no record of **{country}**.", ephemeral=True)
            return

        tier = data["economy"]["tier"]
        value = data["economy"]["value"]

        closest_tier = None
        direction = None
        points_required = None

        for t, (low, high) in ECONOMY_TIERS.items():
            if t == tier:
                if value == high and tier != "Economic Singularity":
                    next_index = list(ECONOMY_TIERS).index(t) + 1
                    next_name = list(ECONOMY_TIERS)[next_index]
                    next_low = ECONOMY_TIERS[next_name][0]
                    closest_tier = next_name
                    direction = "improvement"
                    points_required = next_low - value
                elif value == low and tier != "Collapsed":
                    prev_index = list(ECONOMY_TIERS).index(t) - 1
                    prev_name = list(ECONOMY_TIERS)[prev_index]
                    prev_high = ECONOMY_TIERS[prev_name][1]
                    closest_tier = prev_name
                    direction = "degradation"
                    points_required = value - prev_high
                break

        description = f"**Tier:** {tier}\n*Current Score:* {value}"
        if closest_tier:
            description += f"\nClosest tier shift: **{direction.title()}** to *{closest_tier}* — {points_required} points needed."

        embed = discord.Embed(
            title=f"💰 Economy of {country}",
            description=description,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # === Country Info Command ===
    @app_commands.command(name="countryinfo", description="View full public details about a registered country.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def countryinfo(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ The Archivist finds no record of **{country}**.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📘 Country Profile: {country}",
            description=f"**Leader:** {data['leader']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🛡 Military", value=data["military_strength"]["tier"], inline=True)
        embed.add_field(name="💰 Economy", value=data["economy"]["tier"], inline=True)
        embed.add_field(name="🏛 Stability", value=data["stability"]["tier"], inline=True)
        embed.add_field(name="🧠 Morale", value=data["morale"], inline=True)
        embed.add_field(name="📦 Supply", value=data["supply"], inline=True)

        if data.get("composition"):
            embed.add_field(name="🪖 Unit Composition", value=data["composition"], inline=False)
        if data.get("tags"):
            embed.add_field(name="🏷 Tags", value=", ".join(data["tags"]), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    # === Refined Tier Check Commands ===
    def get_shift_details(current_tier, current_value, tiers):
        closest_tier = None
        direction = None
        points_required = None

        for t, (low, high) in tiers.items():
            if t == current_tier:
                if current_value == high and t != list(tiers)[-1]:
                    next_index = list(tiers).index(t) + 1
                    next_name = list(tiers)[next_index]
                    next_low = tiers[next_name][0]
                    closest_tier = next_name
                    direction = "improvement"
                    points_required = next_low - current_value
                elif current_value == low and t != list(tiers)[0]:
                    prev_index = list(tiers).index(t) - 1
                    prev_name = list(tiers)[prev_index]
                    prev_high = tiers[prev_name][1]
                    closest_tier = prev_name
                    direction = "degradation"
                    points_required = current_value - prev_high
                break

        return closest_tier, direction, points_required

    @app_commands.command(name="checkstability", description="Check a country's stability tier.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checkstability(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        tier = data["stability"]["tier"]
        value = data["stability"]["value"]
        closest_tier, direction, points_required = get_shift_details(tier, value, STABILITY_TIERS)

        desc = f"**Tier:** {tier}\n*Current Score:* {value}"
        if closest_tier:
            desc += f"\nClosest tier shift: **{direction.title()}** to *{closest_tier}* — {points_required} points needed."

        embed = discord.Embed(
            title=f"🏛 Stability of {country}",
            description=desc,
            color=discord.Color.dark_gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checkmoral", description="Check a country's troop morale.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checkmoral(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        morale = data["morale"]
        for tier, (low, high) in MORALE_TIERS.items():
            if low <= morale <= high:
                closest_tier, direction, points_required = get_shift_details(tier, morale, MORALE_TIERS)
                break

        desc = f"*Current Morale:* {morale} ({tier})"
        if closest_tier:
            desc += f"\nClosest tier shift: **{direction.title()}** to *{closest_tier}* — {points_required} points needed."

        embed = discord.Embed(
            title=f"🧠 Morale of {country}",
            description=desc,
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checksupply", description="Check a country's supply levels.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checksupply(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        supply = data["supply"]
        for tier, (low, high) in SUPPLY_TIERS.items():
            if low <= supply <= high:
                closest_tier, direction, points_required = get_shift_details(tier, supply, SUPPLY_TIERS)
                break

        desc = f"*Current Supply:* {supply} ({tier})"
        if closest_tier:
            desc += f"\nClosest tier shift: **{direction.title()}** to *{closest_tier}* — {points_required} points needed."

        embed = discord.Embed(
            title=f"📦 Supply Levels of {country}",
            description=desc,
            color=discord.Color.teal()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checkmilitary", description="Check a country's military strength tier.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checkmilitary(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        tier = data["military_strength"]["tier"]
        embed = discord.Embed(
            title=f"🛡 Military Strength of {country}",
            description=f"**Tier:** {tier}\n*Further details remain in classified files.*",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checktags", description="Check any tags associated with a country.")
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def checktags(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        tags = data.get("tags", [])
        tag_text = ", ".join(tags) if tags else "No tags assigned."

        embed = discord.Embed(
            title=f"🏷 Tags for {country}",
            description=tag_text,
            color=discord.Color.greyple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CountryQueries(bot))
