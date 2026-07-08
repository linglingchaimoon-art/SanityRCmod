import os
import re
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

SANITY_API_URL = os.getenv(
   "SANITY_API_URL",
   "https://sanityrc-production.up.railway.app"
).rstrip("/")

SANITY_API_KEY = os.getenv("SANITY_API_KEY", "test123")


class ReportModal(discord.ui.Modal, title="Create Player Report"):
   target_player = discord.ui.TextInput(
       label="Target Player",
       placeholder="Player name / gamertag",
       required=True,
       max_length=100,
   )

   reason = discord.ui.TextInput(
       label="Reason",
       placeholder="Explain what happened",
       style=discord.TextStyle.paragraph,
       required=True,
       max_length=1000,
   )

   server_name = discord.ui.TextInput(
       label="Server Name",
       placeholder="SANITY2X",
       required=False,
       default="SANITY2X",
       max_length=100,
   )

   def __init__(self, cog):
       super().__init__()
       self.cog = cog

   async def on_submit(self, interaction: discord.Interaction):
       await interaction.response.defer(ephemeral=True)

       payload = {
           "server_name": self.server_name.value or "SANITY2X",
           "reporter_discord": f"{interaction.user} ({interaction.user.id})",
           "target_player": self.target_player.value,
           "reason": self.reason.value,
           "evidence": "No evidence submitted yet.",
       }

       try:
           async with aiohttp.ClientSession() as session:
               async with session.post(
                   f"{SANITY_API_URL}/reports/create",
                   json=payload,
                   headers={
                       "x-api-key": SANITY_API_KEY,
                       "Content-Type": "application/json",
                   },
                   timeout=20,
               ) as response:
                   try:
                       data = await response.json()
                   except Exception:
                       text = await response.text()
                       data = {"detail": text}

                   if response.status >= 400:
                       await interaction.followup.send(
                           f"❌ Could not submit report: `{data}`",
                           ephemeral=True,
                       )
                       return

       except Exception as e:
           await interaction.followup.send(
               f"❌ Could not submit report: `{e}`",
               ephemeral=True,
           )
           return

       report_id = data.get("report_id", "Unknown")

       embed = discord.Embed(
           title="✅ Report Submitted",
           description="The report has been sent to the Sanity RC admin panel.",
           color=discord.Color.green(),
       )

       embed.add_field(name="Report ID", value=str(report_id), inline=True)
       embed.add_field(name="Target Player", value=self.target_player.value, inline=False)
       embed.add_field(name="Reason", value=self.reason.value, inline=False)
       embed.add_field(name="Reporter", value=interaction.user.mention, inline=True)
       embed.add_field(name="Server", value=self.server_name.value or "SANITY2X", inline=True)

       embed.set_footer(text="Sanity RC Reports System")

       await interaction.followup.send(embed=embed, ephemeral=True)


class Reports(commands.Cog):
   def __init__(self, bot):
       self.bot = bot

   @app_commands.command(name="reporttest", description="Test reports cog")
   async def reporttest(self, interaction: discord.Interaction):
       await interaction.response.send_message(
           "Reports cog is working.",
           ephemeral=True,
       )

   @app_commands.command(
       name="report",
       description="Submit a player report to the Sanity RC admin panel."
   )
   async def report(self, interaction: discord.Interaction):
       await interaction.response.send_modal(ReportModal(self))


async def setup(bot):
   await bot.add_cog(Reports(bot))