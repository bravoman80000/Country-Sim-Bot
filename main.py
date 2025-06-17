import os
import discord # type: ignore
from discord.ext import commands # type: ignore

from utils import setup_logging
import modules.war.war_commands
import modules.misc
import modules.war.war_view
import modules.war.war_ledger
import modules.civil.country_queries
import modules.civil.country_register
from modules.civil.year_tracker import start_new_turn

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user}! The Archivist awaits...")


async def main():
    setup_logging()

    # Sync regular (non-async) cogs
    modules.war.war_commands.setup(bot)
    modules.misc.setup(bot)
    modules.war.war_view.setup(bot)
    modules.war.war_ledger.setup(bot)

    # Sync async cogs
    await modules.civil.country_queries.setup(bot)
    await modules.civil.country_register.setup(bot)

    # Slash sync comes LAST
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

    await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
