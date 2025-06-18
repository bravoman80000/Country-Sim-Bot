import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import os
import json
import random

DATA_PATH = "/data/countries.json"

# === Load Countries Safely ===
def load_countries():
    # Ensure file exists before trying to read it
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)  # Start with an empty dict if file is missing

    with open(DATA_PATH, "r") as f:
        return json.load(f)

# === Save Countries ===
def save_countries(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

# === Country Name Autocomplete (for slash commands) ===
async def autocomplete_country_names(interaction: Interaction, current: str):
    data = load_countries()
    return [
        app_commands.Choice(name=name, value=name)
        for name in data
        if current.lower() in name.lower()
    ][:25]  # Discord's autocomplete limit


class CountryModifiers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === Generic Modifier Command Generator ===
    async def modify_stat(self, interaction, country, category, amount, method):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ No record of **{country}** found.", ephemeral=True)
            return

        # GM check
        if not any(role.name == "GM (Game Managers)" for role in interaction.user.roles):
            await interaction.response.send_message("❌ Only GMs may alter the course of nations.", ephemeral=True)
            return

        if method == "roll":
            result = random.randint(1, amount)
        else:
            result = amount

        # Apply change
        stat_path = category.split(".")
        target = data
        for key in stat_path[:-1]:
          target = target[key]
        target_field = stat_path[-1]

        # 🛡 Safe numeric check
        if isinstance(target.get(target_field), (int, float)):
           target[target_field] += result
        else:
          target[target_field] = result  # fallback assignment if the field isn't a number

        # Update file
        countries[country] = data
        save_countries(countries)

        await interaction.response.send_message(
          f"📈 {category.replace('.', ' ').title()} for **{country}** modified by **{result}**.",
         ephemeral=False
        )

        await interaction.user.send(f"🕵️ GM Log: {country}'s {category} is now {target[target_field]}")


    # === /eco Command ===
    @app_commands.command(name="eco", description="GM: Modify a country's economy score.")
    @app_commands.describe(country="The target country", amount="Amount to modify", method="Flat or Roll")
    @app_commands.choices(method=[
        app_commands.Choice(name="Flat", value="flat"),
        app_commands.Choice(name="Roll (1dX)", value="roll")
    ])
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def eco(self, interaction: discord.Interaction, country: str, amount: int, method: app_commands.Choice[str]):
        await self.modify_stat(interaction, country, "economy.value", amount, method.value)

    # === /stability Command ===
    @app_commands.command(name="stability", description="GM: Modify a country's stability score.")
    @app_commands.describe(country="The target country", amount="Amount to modify", method="Flat or Roll")
    @app_commands.choices(method=[
        app_commands.Choice(name="Flat", value="flat"),
        app_commands.Choice(name="Roll (1dX)", value="roll")
    ])
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def stability(self, interaction: discord.Interaction, country: str, amount: int, method: app_commands.Choice[str]):
        await self.modify_stat(interaction, country, "stability.value", amount, method.value)

    # === /moral Command ===
    @app_commands.command(name="moral", description="GM: Modify a country's morale.")
    @app_commands.describe(country="The target country", amount="Amount to modify", method="Flat or Roll")
    @app_commands.choices(method=[
        app_commands.Choice(name="Flat", value="flat"),
        app_commands.Choice(name="Roll (1dX)", value="roll")
    ])
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def moral(self, interaction: discord.Interaction, country: str, amount: int, method: app_commands.Choice[str]):
        await self.modify_stat(interaction, country, "morale", amount, method.value)

    # === /supply Command ===
    @app_commands.command(name="supply", description="GM: Modify a country's supply level.")
    @app_commands.describe(country="The target country", amount="Amount to modify", method="Flat or Roll")
    @app_commands.choices(method=[
        app_commands.Choice(name="Flat", value="flat"),
        app_commands.Choice(name="Roll (1dX)", value="roll")
    ])
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def supply(self, interaction: discord.Interaction, country: str, amount: int, method: app_commands.Choice[str]):
        await self.modify_stat(interaction, country, "supply", amount, method.value)
            # === /military Command ===
            
    @app_commands.command(name="military", description="GM: Modify a country's military value (hidden score, not tier directly).")
    @app_commands.describe(country="The target country", amount="Amount to modify", method="Flat or Roll")
    @app_commands.choices(method=[
        app_commands.Choice(name="Flat", value="flat"),
        app_commands.Choice(name="Roll (1dX)", value="roll")
    ])
    @app_commands.autocomplete(country=autocomplete_country_names)
    async def military(self, interaction: discord.Interaction, country: str, amount: int, method: app_commands.Choice[str]):
        await self.modify_stat(interaction, country, "military_strength.value", amount, method.value)


async def setup(bot):
    await bot.add_cog(CountryModifiers(bot))
