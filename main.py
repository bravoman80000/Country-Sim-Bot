# main.py
from keepalive import keep_alive
import discord
from discord.ext import commands

from config import TOKEN
from utils import setup_logging
import modules.war_commands
import modules.misc
import modules.war_view
import modules.war_ledger
from modules.year_tracker import start_new_turn

# Bot setup
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


# Load command groups
modules.war_commands.setup(bot)
modules.misc.setup(bot)
modules.war_view.setup(bot)
modules.war_ledger.setup(bot)

# Run the bot
# Run the bot
if __name__ == "__main__":
    keep_alive()  # <-- Starts the webserver
    setup_logging()  # <-- Sets up logging
    bot.run(TOKEN)  # <-- Runs the bot
