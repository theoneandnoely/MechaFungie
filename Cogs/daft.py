import discord
from discord import app_commands
from discord.ext import commands
from DaftScraper.campaigns import active_campaigns, add_campaign, deactivate_campaign

class Daft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Daft cog loaded.')

    @app_commands.command(name="test_embed", description="Test sending an embedded message")
    async def test_embed(self, interaction:discord.Interaction, member:discord.Member) -> None:
        embedded_msg = discord.Embed(title = "Test", colour=discord.Colour.dark_green())
        embedded_msg.set_thumbnail(url=interaction.guild.icon)
        embedded_msg.add_field(name="User", value=member.display_name, inline=True)
        embedded_msg.add_field(name="Status", value=interaction.guild.get_member(member.id).status, inline=True)
        embedded_msg.set_image(url=member.avatar)
        await interaction.response.send_message(embed=embedded_msg)
        return

    @app_commands.command(name="add_daft_campaign", description="Adds a new campaign for the daft scraper to post notifications for")
    @app_commands.describe(member_1="This user will be @ mentioned for each post for this campaign")
    @app_commands.describe(member_2="This user will be @ mentioned for each post for this campaign")
    @app_commands.describe(member_3="This user will be @ mentioned for each post for this campaign")
    async def add_daft_campaign(self, interaction:discord.Interaction, num_beds:int, max_price:float, member_1:discord.Member=None, member_2:discord.Member=None, member_3:discord.Member=None) -> None:
        members = []
        if member_1 is not None:
            members.append(member_1)
        if member_2 is not None:
            members.append(member_2)
        if member_3 is not None:
            members.append(member_3)
        id = add_campaign(num_beds, max_price, members)
        await interaction.response.send_message(f'Campaign created with ID: {id}!')
        return
    
    @app_commands.command(name="active_daft_campaigns", description="Lists currently active daft scraper campaigns")
    async def active_daft_campaigns(self, interaction:discord.Interaction) -> None:
        output = active_campaigns()
        ids_list = output[0]
        if len(ids_list) == 0:
            await interaction.response.send_message("No active campaigns.\nStart a new campaign with the `/add_daft_campaign` command!")
            return
        else:
            ids = f'{ids_list[0]}'
            for i in range(1,len(ids_list)):
                ids = ids + f'\n{ids_list[i]}'
            beds = f'{output[1][0]}'
            for j in range(1,len(output[1])):
                beds = beds + f'\n{output[1][j]}'
            prices = f'{output[2][0]}'
            for k in range(1, len(output[2])):
                prices = prices + f'\n{output[2][k]}'
            campaigns_embed = discord.Embed(title = "Active Campaigns", colour=discord.Colour.dark_gold())
            campaigns_embed.add_field(name="ID", value=ids, inline=True)
            campaigns_embed.add_field(name="Beds", value=beds, inline=True)
            campaigns_embed.add_field(name="Max Price", value=prices, inline=True)
            await interaction.response.send_message(embed=campaigns_embed)
            return
        
    @app_commands.command(name="deactivate_daft_campaign", description="Deactivate the daft campaign with the specified ID")
    @app_commands.describe(id="The ID of the campaign to be deactivated. To find the list of ids for active campaigns use the /active_daft_campaigns command")
    async def deactivate_daft_campaign(self, interaction:discord.Interaction, id:int):
        deactivate_campaign(id)
        await interaction.response.send_message(f'Campaign ID {id} succefully deactivated.')
        return

async def setup(bot):
    await bot.add_cog(Daft(bot))