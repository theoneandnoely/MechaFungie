import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), application_id='1245794539378053241')

@bot.event
async def on_ready():
    print("Mecha Fungie is Online")

@bot.command()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f'Synced {len(synced)} command(s)!')
    except Exception as e:
        print(e)

async def load():
    for file in os.listdir('./Cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'Cogs.{file[:-3]}')

@bot.tree.command(name="opinion")
async def opinion(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} is a piece of shit!")

async def main():
    await load()
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
