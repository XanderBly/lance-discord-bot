import discord
from discord.ext import commands, tasks
from discord.utils import get
import random
import json
import os

# INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ID del Leader e Vice (da aggiornare con quelli reali)
LEADER_ID = 123456789012345678
VICELEADER_ID = 234567890123456789

# File JSON nomi
NOMI_FILE = 'nomi_in_game.json'
if os.path.exists(NOMI_FILE):
    with open(NOMI_FILE, 'r', encoding='utf-8') as f:
        nomi_in_game = json.load(f)
else:
    nomi_in_game = {}

# Lista di bevande
bevande = [
    "Vi ho servito del vino rosso d'annata, Altezza. 🍷",
    "Ecco del tè imperiale, caldo e profumato come si addice a Vostra Maestà. 🍵",
    "Una coppa di idromele, degna di un regno prospero. 🏰",
    "Dell'acqua pura di sorgente, la bevanda della disciplina. 💧",
    "Un elisir speziato, per rinvigorire le membra regali. 🧪"
]

# Parole vietate
parole_vietate = ["cazzo", "merda", "stronzo", "puttana"]

@bot.event
async def on_ready():
    print(f'{bot.user} è ora online e al servizio della Corte.')
    remind_name_check.start()

@bot.command(name='bevi')
async def serve_bevanda(ctx):
    scelta = random.choice(bevande)
    await ctx.send(f"{ctx.author.mention} {scelta}")

@bot.command(name='help')
async def mostra_comandi(ctx):
    comandi = (
        f"📜 *Altezza {ctx.author.display_name}, ecco l'elenco delle mie umili mansioni a corte:*\n\n"
        "🔹 `!bevi` – Vi servirò personalmente una bevanda degna del vostro rango.\n"
        "🔹 *(automatico)* – Vi ammonirò cortesemente se il vostro linguaggio dovesse risultare sconveniente.\n"
        "🔹 *(automatico)* – Ricorderò ai nuovi arrivati di annunciare il proprio nome in gioco.\n"
        "🔹 *(automatico)* – Notificherò con rispetto se Sua Altezza Reale o il Vice vengono evocati durante la loro assenza.\n"
        "🔹 `!nome @utente` – Rivelerò, con deferenza, il nome in gioco di un cortigiano.\n"
        "🔹 `!comandi` – La lista ordinata dei comandi disponibili.\n\n"
        "In ogni cosa, rimango al vostro servizio con devozione. 🤴"
    )
    await ctx.send(comandi)

@bot.command(name='comandi')
async def elenco_comandi(ctx):
    elenco = (
        f"📚 *Altezza {ctx.author.display_name}, questi sono i comandi che potete usare a Corte:*\n\n"
        "🧉 `!bevi` – Riceverete una bevanda regale.\n"
        "🛠️ `!help` – Scoprite le funzioni del vostro umile servitore.\n"
        "📋 `!comandi` – Questa lista di comandi utilizzabili.\n"
        "📛 `!nome @utente` – Rivela il nome in gioco registrato.\n\n"
        "Vi auguro una permanenza degna del vostro rango."
    )
    await ctx.send(elenco)

@bot.command(name='nome')
async def mostra_nome_in_game(ctx, membro: discord.Member):
    nome = nomi_in_game.get(str(membro.id))
    if nome:
        await ctx.send(f"{membro.display_name} è conosciuto in gioco come **{nome}**.")
    else:
        await ctx.send(f"Altezza, non ho trovato il nome in gioco di {membro.display_name}.")

@bot.event
async def on_member_join(member):
    canale = get(member.guild.text_channels, name="welcome")
    if canale:
        await canale.send(f"Benvenutə {member.mention}. Qual è il vostro nome in gioco, Altezza?")

    ruolo = get(member.guild.roles, name="Vassalli")
    if ruolo:
        await member.add_roles(ruolo)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "welcome" and not message.author.bot:
        contenuto = message.content.strip()
        if contenuto:
            nomi_in_game[str(message.author.id)] = contenuto
            with open(NOMI_FILE, 'w', encoding='utf-8') as f:
                json.dump(nomi_in_game, f, ensure_ascii=False, indent=2)
            await message.channel.send(f"Registrato, {message.author.mention}. Ricorderò che siete conosciuti in gioco come **{contenuto}**.")

    if any(parola in message.content.lower() for parola in parole_vietate):
        await message.channel.send(
            f"Perdonatemi, Altezza {message.author.mention}... ma il vostro linguaggio non è accettabile. Vi invito alla moderazione considerando dove vi trovate."
        )

    if message.mentions:
        for utente in message.mentions:
            if utente.id in [LEADER_ID, VICELEADER_ID] and utente.status != discord.Status.online:
                await message.channel.send(
                    f"Vi prego di attendere, {message.author.mention}. Sua Altezza Reale {utente.display_name} non è al momento presente nella Sala del Trono."
                )

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    await on_message(after)

@tasks.loop(hours=12)
async def remind_name_check():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue
            if str(member.id) not in nomi_in_game:
                try:
                    await member.send("Altezza, ricordate di dichiarare il vostro nome in gioco nel canale di benvenuto.")
                except discord.Forbidden:
                    pass

# Avvia il bot leggendo il token dal file .env
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("⚠️ TOKEN mancante. Assicurati che il file .env contenga la variabile DISCORD_TOKEN.")
else:
    bot.run(TOKEN)
