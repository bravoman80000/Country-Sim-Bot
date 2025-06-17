import discord
from discord.ext import commands
import os
import json
import io

DATA_PATH = os.path.join("data", "countries.json")

def load_countries():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_countries(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

class DebugCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !dumpjson — Dump all countries JSON as a file
    @commands.command(name="!dumpjson")
    async def dump_json(self, ctx):
        if not any(role.name == "GM (Game Manager)" for role in ctx.author.roles):
            await ctx.send("❌ You do not have permission to run debug commands.")
            return

        countries = load_countries()
        json_text = json.dumps(countries, indent=2)
        await ctx.send(file=discord.File(io.StringIO(json_text), filename="countries_debug.json"))

    # !dumpcountry <Country Name> — View specific country JSON
    @commands.command(name="!dumpcountry")
    async def dump_country(self, ctx, *, country: str):
        if not any(role.name == "GM (Game Manager)" for role in ctx.author.roles):
            await ctx.send("❌ You do not have permission to run debug commands.")
            return

        countries = load_countries()
        if country not in countries:
            await ctx.send(f"❌ Country `{country}` not found.")
            return

        data = json.dumps(countries[country], indent=2)
        if len(data) < 1900:
            await ctx.send(f"```json\n{data}```")
        else:
            await ctx.send(file=discord.File(io.StringIO(data), filename=f"{country}_debug.json"))

    # !listcountries — List all country names
    @commands.command(name="!listcountries")
    async def list_countries(self, ctx):
        countries = load_countries()
        names = ", ".join(countries.keys())
        await ctx.send(f"🌍 **Registered Countries** ({len(countries)}):\n{names}")

    # !resetcountry <Country Name> — Reset a single country to defaults
    @commands.command(name="!resetcountry")
    async def reset_country(self, ctx, *, country: str):
        if not any(role.name == "GM (Game Manager)" for role in ctx.author.roles):
            await ctx.send("❌ You do not have permission to run debug commands.")
            return

        countries = load_countries()
        if country not in countries:
            await ctx.send(f"❌ Country `{country}` not found.")
            return

        countries[country] = {
            "leader": "Unknown",
            "military_strength": {"tier": "Trivial"},
            "economy": {"tier": "Collapsed", "value": 0},
            "stability": {"tier": "Revolution", "value": 0},
            "morale": 50,
            "supply": 50,
            "composition": "Unknown",
            "tags": []
        }
        save_countries(countries)
        await ctx.send(f"🔁 `{country}` has been reset to defaults.")

async def setup(bot):
    await bot.add_cog(DebugCommands(bot))
