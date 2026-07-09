import os
import discord
from discord.ext import commands

TOKEN = os.getenv("MTUyNDQzOTkyNTYxNTg4NjU1Nw.Golajf.zQIADQDCbD3Cm3kLIz5fftIsMyKtjoFbM_u_pg")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ======================
# START BOTA
# ======================

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    bot.add_view(TicketPanel())
    bot.add_view(CloseButton())
    bot.add_view(PartnerView())


# ======================
# TICKETY
# ======================

class TicketPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    async def create_ticket(self, interaction, typ):

        guild = interaction.guild
        user = interaction.user

        nazwa = f"ticket-{user.name}"


        for c in guild.text_channels:
            if c.name == nazwa:
                await interaction.response.send_message(
                    "Masz już ticket!",
                    ephemeral=True
                )
                return


        category = discord.utils.get(
            guild.categories,
            name=typ
        )


        if category is None:
            category = await guild.create_category(typ)


        overwrites = {
            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
        }


        channel = await guild.create_text_channel(
            nazwa,
            category=category,
            overwrites=overwrites
        )


        if typ == "Pomoc":

            tekst = "🛠️ Opisz swój problem."

        else:

            tekst = "🤝 Opisz swój serwer i wyślij link do niego."


        embed = discord.Embed(
            title=f"🎫 {typ}",
            description=f"{user.mention}\n\n{tekst}",
            color=discord.Color.blue()
        )


        await channel.send(
            embed=embed,
            view=CloseButton()
        )


        await interaction.response.send_message(
            f"Utworzono {channel.mention}",
            ephemeral=True
        )



    @discord.ui.button(
        label="🛠️ Pomoc",
        style=discord.ButtonStyle.blurple,
        custom_id="pomoc"
    )
    async def pomoc(self, interaction, button):

        await self.create_ticket(
            interaction,
            "Pomoc"
        )


    @discord.ui.button(
        label="🤝 Partnerstwo",
        style=discord.ButtonStyle.green,
        custom_id="partner"
    )
    async def partner(self, interaction, button):

        await self.create_ticket(
            interaction,
            "Partnerstwo"
        )



class CloseButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="🔒 Zamknij",
        style=discord.ButtonStyle.red,
        custom_id="close"
    )
    async def close(self, interaction, button):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "Brak uprawnień!",
                ephemeral=True
            )

            return


        await interaction.channel.delete()



@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):

    embed = discord.Embed(
        title="🎫 Tickety",
        description=(
            "Wybierz opcję:\n\n"
            "🛠️ Pomoc\n"
            "🤝 Partnerstwo"
        ),
        color=discord.Color.blue()
    )


    await ctx.send(
        embed=embed,
        view=TicketPanel()
    )



# ======================
# PARTNERSTWO FORMULARZ
# ======================

class PartnerModal(discord.ui.Modal, title="Partnerstwo"):

    opis = discord.ui.TextInput(
        label="Opisz swój serwer",
        style=discord.TextStyle.paragraph
    )

    link = discord.ui.TextInput(
        label="Link do serwera",
        placeholder="https://discord.gg/..."
    )


    async def on_submit(self, interaction):

        kanal = discord.utils.get(
            interaction.guild.text_channels,
            name="partnerstwa"
        )


        if kanal is None:
            kanal = await interaction.guild.create_text_channel(
                "partnerstwa"
            )


        embed = discord.Embed(
            title="🤝 Nowe partnerstwo",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Autor",
            value=interaction.user.mention
        )

        embed.add_field(
            name="Opis",
            value=self.opis.value,
            inline=False
        )

        embed.add_field(
            name="Link",
            value=self.link.value,
            inline=False
        )


        await kanal.send(embed=embed)


        await interaction.response.send_message(
            "Wysłano do administracji!",
            ephemeral=True
        )



class PartnerView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="🤝 Wyślij partnerstwo",
        style=discord.ButtonStyle.green,
        custom_id="partner_form"
    )
    async def button(self, interaction, button):

        await interaction.response.send_modal(
            PartnerModal()
        )



@bot.command()
async def partnerstwo(ctx):

    embed = discord.Embed(
        title="🤝 Partnerstwo",
        description="Kliknij przycisk i wyślij swoje partnerstwo.",
        color=discord.Color.green()
    )


    await ctx.send(
        embed=embed,
        view=PartnerView()
    )



# ======================
# ADMIN
# ======================

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, liczba:int):

    await ctx.channel.purge(
        limit=liczba+1
    )

    await ctx.send(
        "Usunięto wiadomości",
        delete_after=3
    )


# ======================

bot.run(TOKEN)