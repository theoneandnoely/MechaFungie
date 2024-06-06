import discord
from discord.ext import commands

class Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Stag", emoji="🟥", description="Stag role"),
            discord.SelectOption(label="Prick", emoji="🟦", description="Prick role")
        ]
        super().__init__(placeholder="Choose your role", max_values = 1, min_values = 1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        if self.values[0] == "Stag":
            role = await guild.create_role(name="Stag", colour=discord.Colour.red())
            await user.edit(roles = [role])
            await interaction.response.send_message("Good man yourself", ephemeral = True)
        elif self.values[0] == "Prick":
            role = await guild.create_role(name="Prick", colour=discord.Colour.blue())
            await user.edit(roles = [role])
            await interaction.response.send_message(f"Congrats, {interaction.user.mention} is a Leinster prick", ephemeral=False)

class SelectView(discord.ui.View):
    def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(Select())

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Role cog is ready!')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx):
        await ctx.send("Pick a role", view=SelectView(), delete_after=15)

async def setup(bot):
    await bot.add_cog(Role(bot))