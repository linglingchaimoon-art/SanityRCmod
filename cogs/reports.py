import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


SANITY_API_URL = os.getenv(
    "SANITY_API_URL",
    "https://sanityrc-production.up.railway.app"
)

SANITY_API_KEY = os.getenv("SANITY_API_KEY", "test123")


class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        
    @app_commands.command(name="reporttest", description="Test reports cog")
    async def reporttest(self, interaction: discord.Interaction):
        await interaction.response.send_message("Reports cog is working.", ephemeral=True)

    @app_commands.command(
        name="report",
        description="Submit a player report to the Sanity RC admin panel."
    )
    @app_commands.describe(
        target_player="Player name or gamertag you want to report",
        reason="Why are you reporting this player?",
        evidence="Optional clip/image/link as evidence",
        server_name="Optional server name"
    )
    async def report(
        self,
        interaction: discord.Interaction,
        target_player: str,
        reason: str,
        evidence: str | None = None,
        server_name: str | None = "SANITY2X",
    ):
        await interaction.response.defer(ephemeral=True)

        payload = {
            "server_name": server_name,
            "reporter_discord": f"{interaction.user} ({interaction.user.id})",
            "target_player": target_player,
            "reason": reason,
            "evidence": evidence,
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
                    data = await response.json()

                    if response.status >= 400:
                        await interaction.followup.send(
                            f":x: Report failed: `{data}`",
                            ephemeral=True,
                        )
                        return

        except Exception as e:
            await interaction.followup.send(
                f":x: Could not submit report: `{e}`",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=":rotating_light: Report Submitted",
            description="Your report has been sent to the Sanity RC admin panel.",
            color=discord.Color.red(),
        )

        embed.add_field(name="Target Player", value=target_player, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Reporter", value=interaction.user.mention, inline=True)
        embed.add_field(name="Server", value=server_name or "Unknown", inline=True)

        if evidence:
            embed.add_field(name="Evidence", value=evidence, inline=False)

        embed.set_footer(text=f"Report ID: {data.get('report_id', 'Unknown')}")

        await interaction.followup.send(embed=embed, ephemeral=True)




async def setup(bot):
    await bot.add_cog(Reports(bot))