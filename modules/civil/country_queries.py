import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
import os
import json

DATA_PATH = os.path.join("data", "countries.json")

def load_countries():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

class CountryQueries(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="checkeco", description="Check a country's economic tier.")
    async def checkeco(self, interaction: discord.Interaction, country: str):
        countries = load_countries()
        data = countries.get(country)

        if not data:
            await interaction.response.send_message(f"❌ The Archivist finds no record of **{country}**.", ephemeral=True)
            return

        tier = data["economy"]["tier"]
        embed = discord.Embed(
            title=f"💰 Economy of {country}",
            description=f"**Tier:** {tier}\n*Further details remain sealed in the Archives.*",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CountryQueries(bot))
