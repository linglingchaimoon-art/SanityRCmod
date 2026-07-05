import os
import asyncio
import itertools
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

statuses = itertools.cycle([
    discord.Activity(type=discord.ActivityType.listening, name="Coming soon!"),
])


@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(
        status=discord.Status.online,
        activity=next(statuses)
    )


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    if not change_status.is_running():
        change_status.start()


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


asyncio.run(main())