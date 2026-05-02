"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

Virtual Enhanced General Assistant
Discord Assistant Bot — Version 1.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTALLATION :
  pip install discord.py aiohttp pytz yt-dlp PyNaCl

CONFIGURATION :
  1. Remplace TON_TOKEN_ICI par ton token Discord
  2. Active : Message Content Intent + Server Members Intent
  3. Lance : python jarvis.py

COMMANDES SLASH :
  /aide          → Toutes les commandes
  /setup         → Créer un serveur Discord complet
  /reset         → Annuler le setup en cours
  /heure         → Heure dans n'importe quel pays/ville
  /meteo         → Météo d'une ville
  /cherche       → Recherche sur le web (liens + résumé)
  /calcul        → Calculatrice avancée
  /traduit       → Traduire un texte
  /couleur       → Infos sur une couleur HEX
  /avatar        → Avatar d'un membre
  /serverinfo    → Infos sur le serveur
  /userinfo      → Infos sur un utilisateur
  /rappel        → Rappel dans X minutes
  /tirage        → Tirage au sort parmi des options
  /qr            → Générer un QR code

COMMANDES TEXTE (préfixe !) :
  !jarvis [question] → Parler à JARVIS (IA conversationnelle)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import math
import re
import json
import urllib.parse
from datetime import datetime, timezone
import pytz
from discord.ext import tasks
import random
import os
from dotenv import load_dotenv
load_dotenv()

# ═══════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
PREFIX = "!"
VEGA_COLOR = 0x00D4FF   # Bleu VEGA
VEGA_VERSION = "2.0"

# ═══════════════════════════════════════════
#  PERSONNALITÉ VEGA
# ═══════════════════════════════════════════

VEGA_QUOTES = [
    "À votre service.",
    "Calcul en cours...",
    "Bien reçu.",
    "Je suis là pour vous assister.",
    "Traitement de votre requête.",
    "Mes systèmes sont en ligne.",
    "Analyse complète.",
    "Opération effectuée avec succès.",
]

VEGA_ERRORS = [
    "Je ne suis pas en mesure de traiter cette requête.",
    "Mes systèmes ont rencontré une anomalie.",
    "Requête invalide. Veuillez reformuler.",
    "Données insuffisantes pour répondre.",
]

# ═══════════════════════════════════════════
#  SETUP BOT
# ═══════════════════════════════════════════

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║  VEGA — En ligne                   ║
║  Connecté : {str(bot.user):<26}║
║  Serveurs  : {str(len(bot.guilds)):<26}║
╚══════════════════════════════════════╝
    """)
    try:
        synced = await bot.tree.sync()
        print(f"  ✅ {len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
        print(f"  ❌ Erreur sync : {e}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/aide • VEGA v1.0"
        )
    )

# ═══════════════════════════════════════════
#  HELPER — Embed VEGA
# ═══════════════════════════════════════════

def vega_embed(title: str, description: str = "", color=None, footer: str = None) -> discord.Embed:
    embed = discord.Embed(
        title=f"⚡ {title}",
        description=description,
        color=color or VEGA_COLOR
    )
    embed.set_footer(text=footer or f"VEGA v{VEGA_VERSION} • Virtual Enhanced General Assistant")
    return embed

# ═══════════════════════════════════════════
#  /aide
# ═══════════════════════════════════════════

@bot.tree.command(name="aide", description="Affiche toutes les commandes JARVIS")
async def aide(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ VEGA — Manuel de bord",
        description="*Virtual Enhanced General Assistant* • Votre assistant Discord personnel.",
        color=VEGA_COLOR
    )
    embed.add_field(name="🌐 Internet & Infos", value=(
        "`/cherche` — Recherche web avec liens\n"
        "`/heure` — Heure dans n'importe quelle ville\n"
        "`/meteo` — Météo d'une ville\n"
        "`/couleur` — Infos d'une couleur HEX"
    ), inline=False)
    embed.add_field(name="🛠️ Utilitaires", value=(
        "`/calcul` — Calculatrice (formules complexes)\n"
        "`/traduit` — Traduction de texte\n"
        "`/rappel` — Rappel dans X minutes\n"
        "`/tirage` — Tirage au sort\n"
        "`/qr` — Générer un QR code"
    ), inline=False)
    embed.add_field(name="👤 Serveur & Membres", value=(
        "`/serverinfo` — Infos sur ce serveur\n"
        "`/userinfo` — Infos sur un membre\n"
        "`/avatar` — Avatar d'un membre"
    ), inline=False)
    embed.add_field(name="🏗️ Création de serveur", value=(
        "`/setup` — Assistant création de serveur complet\n"
        "`/reset` — Annuler le setup en cours"
    ), inline=False)
    embed.add_field(name="💬 IA Conversationnelle", value=(
        "`!jarvis [question]` — Posez n'importe quelle question à JARVIS"
    ), inline=False)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"VEGA v{VEGA_VERSION} • {len(bot.tree.get_commands())} commandes disponibles")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /heure — Fuseau horaire
# ═══════════════════════════════════════════

TIMEZONE_MAP = {
    # Villes et pays courants → timezone
    "paris": "Europe/Paris", "france": "Europe/Paris",
    "london": "Europe/London", "londres": "Europe/London", "uk": "Europe/London",
    "new york": "America/New_York", "new-york": "America/New_York", "usa": "America/New_York",
    "los angeles": "America/Los_Angeles", "la": "America/Los_Angeles",
    "tokyo": "Asia/Tokyo", "japon": "Asia/Tokyo", "japan": "Asia/Tokyo",
    "dubai": "Asia/Dubai", "emirats": "Asia/Dubai",
    "moscou": "Europe/Moscow", "moscow": "Europe/Moscow", "russie": "Europe/Moscow",
    "beijing": "Asia/Shanghai", "pekin": "Asia/Shanghai", "chine": "Asia/Shanghai",
    "sydney": "Australia/Sydney", "australie": "Australia/Sydney",
    "toronto": "America/Toronto", "canada": "America/Toronto",
    "berlin": "Europe/Berlin", "allemagne": "Europe/Berlin",
    "madrid": "Europe/Madrid", "espagne": "Europe/Madrid",
    "rome": "Europe/Rome", "italie": "Europe/Rome",
    "amsterdam": "Europe/Amsterdam",
    "bruxelles": "Europe/Brussels", "belgique": "Europe/Brussels",
    "geneve": "Europe/Zurich", "zurich": "Europe/Zurich", "suisse": "Europe/Zurich",
    "montreal": "America/Montreal",
    "miami": "America/New_York",
    "chicago": "America/Chicago",
    "seoul": "Asia/Seoul", "coree": "Asia/Seoul",
    "singapour": "Asia/Singapore", "singapore": "Asia/Singapore",
    "bangkok": "Asia/Bangkok", "thailande": "Asia/Bangkok",
    "cairo": "Africa/Cairo", "le caire": "Africa/Cairo", "egypte": "Africa/Cairo",
    "sao paulo": "America/Sao_Paulo", "bresil": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires", "argentine": "America/Argentina/Buenos_Aires",
    "mexico": "America/Mexico_City",
    "stockholm": "Europe/Stockholm", "suede": "Europe/Stockholm",
    "oslo": "Europe/Oslo", "norvege": "Europe/Oslo",
    "helsinki": "Europe/Helsinki", "finlande": "Europe/Helsinki",
    "varsovie": "Europe/Warsaw", "pologne": "Europe/Warsaw",
    "istanbul": "Europe/Istanbul", "turquie": "Europe/Istanbul",
    "tel aviv": "Asia/Jerusalem", "israel": "Asia/Jerusalem",
    "mumbai": "Asia/Kolkata", "inde": "Asia/Kolkata", "delhi": "Asia/Kolkata",
    "karachi": "Asia/Karachi", "pakistan": "Asia/Karachi",
    "nairobi": "Africa/Nairobi", "kenya": "Africa/Nairobi",
    "lagos": "Africa/Lagos", "nigeria": "Africa/Lagos",
    "casablanca": "Africa/Casablanca", "maroc": "Africa/Casablanca",
    "alger": "Africa/Algiers", "algerie": "Africa/Algiers",
    "tunis": "Africa/Tunis", "tunisie": "Africa/Tunis",
    "dakar": "Africa/Dakar", "senegal": "Africa/Dakar",
    "hawaii": "Pacific/Honolulu",
    "anchorage": "America/Anchorage", "alaska": "America/Anchorage",
    "denver": "America/Denver",
    "phoenix": "America/Phoenix",
    "seattle": "America/Los_Angeles",
    "auckland": "Pacific/Auckland", "nouvelle-zelande": "Pacific/Auckland",
    "jakarta": "Asia/Jakarta", "indonesie": "Asia/Jakarta",
    "manila": "Asia/Manila", "philippines": "Asia/Manila",
    "hong kong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei", "taiwan": "Asia/Taipei",
    "kuala lumpur": "Asia/Kuala_Lumpur", "malaisie": "Asia/Kuala_Lumpur",
}

@bot.tree.command(name="heure", description="Affiche l'heure actuelle dans une ville ou un pays")
@app_commands.describe(lieu="Ville ou pays (ex: Tokyo, Paris, New York...)")
async def heure(interaction: discord.Interaction, lieu: str):
    lieu_lower = lieu.lower().strip()
    tz_name = TIMEZONE_MAP.get(lieu_lower)

    # Essaie de trouver partiellement
    if not tz_name:
        for key, val in TIMEZONE_MAP.items():
            if lieu_lower in key or key in lieu_lower:
                tz_name = val
                break

    # Essaie directement comme timezone pytz
    if not tz_name:
        try:
            pytz.timezone(lieu)
            tz_name = lieu
        except:
            pass

    if not tz_name:
        embed = vega_embed(
            "Heure — Lieu inconnu",
            f"Je ne connais pas **{lieu}**.\n\nEssaie : `Paris`, `Tokyo`, `New York`, `Dubai`, `Sydney`...",
            color=0xE74C3C
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        utc_offset = now.strftime("%z")
        utc_str = f"UTC{utc_offset[:3]}:{utc_offset[3:]}" if len(utc_offset) == 5 else f"UTC{utc_offset}"

        # Emoji heure
        hour = now.hour
        if 6 <= hour < 12:
            time_emoji = "🌅"
        elif 12 <= hour < 18:
            time_emoji = "☀️"
        elif 18 <= hour < 22:
            time_emoji = "🌆"
        else:
            time_emoji = "🌙"

        embed = vega_embed(
            f"Heure — {lieu.title()}",
            f"{time_emoji} **{now.strftime('%H:%M:%S')}**\n"
            f"📅 {now.strftime('%A %d %B %Y')}\n"
            f"🌍 Fuseau : `{tz_name}` ({utc_str})"
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# ═══════════════════════════════════════════
#  /meteo — Météo via wttr.in (sans API key)
# ═══════════════════════════════════════════

@bot.tree.command(name="meteo", description="Météo actuelle d'une ville")
@app_commands.describe(ville="Nom de la ville")
async def meteo(interaction: discord.Interaction, ville: str):
    await interaction.response.defer()
    url = f"https://wttr.in/{urllib.parse.quote(ville)}?format=j1&lang=fr"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    raise Exception("Ville non trouvée")
                data = await resp.json()

        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]

        temp_c = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]
        wind_kmph = current["windspeedKmph"]
        wind_dir = current["winddir16Point"]
        desc = current["lang_fr"][0]["value"] if current.get("lang_fr") else current["weatherDesc"][0]["value"]
        visibility = current["visibility"]
        uv = current["uvIndex"]
        cloud = current["cloudcover"]

        # Emoji météo
        desc_lower = desc.lower()
        if "soleil" in desc_lower or "clair" in desc_lower or "ensoleillé" in desc_lower:
            emoji = "☀️"
        elif "nuage" in desc_lower or "couvert" in desc_lower:
            emoji = "☁️"
        elif "pluie" in desc_lower or "averse" in desc_lower:
            emoji = "🌧️"
        elif "neige" in desc_lower:
            emoji = "❄️"
        elif "orage" in desc_lower or "tonnerre" in desc_lower:
            emoji = "⛈️"
        elif "brouillard" in desc_lower or "brume" in desc_lower:
            emoji = "🌫️"
        elif "partiellement" in desc_lower:
            emoji = "⛅"
        else:
            emoji = "🌡️"

        embed = vega_embed(
            f"Météo — {city_name}, {country}",
            f"{emoji} **{desc}**"
        )
        embed.add_field(name="🌡️ Température", value=f"**{temp_c}°C** (ressenti {feels_like}°C)", inline=True)
        embed.add_field(name="💧 Humidité", value=f"{humidity}%", inline=True)
        embed.add_field(name="💨 Vent", value=f"{wind_kmph} km/h {wind_dir}", inline=True)
        embed.add_field(name="👁️ Visibilité", value=f"{visibility} km", inline=True)
        embed.add_field(name="☁️ Nuages", value=f"{cloud}%", inline=True)
        embed.add_field(name="🔆 Indice UV", value=str(uv), inline=True)

        # Prévisions 3 jours
        weather_days = data.get("weather", [])[:3]
        if weather_days:
            previsions = ""
            jours = ["Aujourd'hui", "Demain", "Après-demain"]
            for i, day in enumerate(weather_days):
                max_t = day["maxtempC"]
                min_t = day["mintempC"]
                previsions += f"**{jours[i]}** : {min_t}°C → {max_t}°C\n"
            embed.add_field(name="📅 Prévisions", value=previsions, inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = vega_embed(
            "Météo — Erreur",
            f"Impossible de récupérer la météo pour **{ville}**.\nVérifie l'orthographe de la ville.",
            color=0xE74C3C
        )
        await interaction.followup.send(embed=embed)

# ═══════════════════════════════════════════
#  /cherche — Recherche web (DuckDuckGo)
# ═══════════════════════════════════════════

@bot.tree.command(name="cherche", description="Recherche sur le web et retourne les meilleurs liens")
@app_commands.describe(requete="Ce que tu veux rechercher")
async def cherche(interaction: discord.Interaction, requete: str):
    await interaction.response.defer()
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(requete)}&format=json&no_html=1&skip_disambig=1"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8),
                                   headers={"User-Agent": "JARVISBot/1.0"}) as resp:
                data = await resp.json(content_type=None)

        embed = vega_embed(f"Recherche — {requete}")

        # Réponse instantanée
        abstract = data.get("AbstractText", "")
        abstract_url = data.get("AbstractURL", "")
        abstract_source = data.get("AbstractSource", "")

        if abstract:
            embed.add_field(
                name=f"📖 {abstract_source}",
                value=f"{abstract[:400]}{'...' if len(abstract) > 400 else ''}\n[Lire la suite]({abstract_url})",
                inline=False
            )

        # Résultats connexes
        related = data.get("RelatedTopics", [])
        links = []
        for item in related[:6]:
            if isinstance(item, dict) and "FirstURL" in item and "Text" in item:
                text = item["Text"][:80]
                url_item = item["FirstURL"]
                links.append(f"🔗 [{text}...]({url_item})")

        if links:
            embed.add_field(name="🌐 Résultats connexes", value="\n".join(links), inline=False)

        # Lien de recherche direct
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(requete)}"
        duckduck_url = f"https://duckduckgo.com/?q={urllib.parse.quote(requete)}"
        embed.add_field(
            name="🔍 Ouvrir dans un navigateur",
            value=f"[Google]({google_url}) • [DuckDuckGo]({duckduck_url}) • [YouTube](https://www.youtube.com/results?search_query={urllib.parse.quote(requete)}) • [Wikipedia](https://fr.wikipedia.org/w/index.php?search={urllib.parse.quote(requete)})",
            inline=False
        )

        if not abstract and not links:
            embed.description = (
                f"Aucun résultat instantané trouvé pour **{requete}**.\n\n"
                f"[Rechercher sur Google]({google_url})\n"
                f"[Rechercher sur DuckDuckGo]({duckduck_url})"
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(requete)}"
        embed = vega_embed(
            f"Recherche — {requete}",
            f"[🔍 Voir les résultats sur Google]({google_url})\n"
            f"[🦆 Voir les résultats sur DuckDuckGo](https://duckduckgo.com/?q={urllib.parse.quote(requete)})"
        )
        await interaction.followup.send(embed=embed)

# ═══════════════════════════════════════════
#  /calcul — Calculatrice
# ═══════════════════════════════════════════

SAFE_MATH = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "log2": math.log2, "exp": math.exp, "abs": abs,
    "ceil": math.ceil, "floor": math.floor, "round": round,
    "pi": math.pi, "e": math.e, "inf": math.inf,
    "pow": pow, "factorial": math.factorial,
}

@bot.tree.command(name="calcul", description="Calculatrice avancée (supporte sin, cos, sqrt, log...)")
@app_commands.describe(expression="Expression mathématique (ex: sqrt(144), sin(pi/2), 2**10)")
async def calcul(interaction: discord.Interaction, expression: str):
    try:
        # Nettoyage et sécurité
        expr_clean = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
        # Bloque les imports et fonctions dangereuses
        forbidden = ["import", "exec", "eval", "open", "os", "__", "subprocess"]
        for f in forbidden:
            if f in expr_clean.lower():
                raise ValueError("Expression non autorisée.")

        result = eval(expr_clean, {"__builtins__": {}}, SAFE_MATH)

        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                result_str = str(int(result))
            else:
                result_str = f"{result:.10g}"
        else:
            result_str = str(result)

        embed = vega_embed(
            "Calculatrice",
            f"```\n{expression} = {result_str}\n```"
        )
        embed.add_field(name="Expression", value=f"`{expression}`", inline=True)
        embed.add_field(name="Résultat", value=f"**{result_str}**", inline=True)
        await interaction.response.send_message(embed=embed)

    except ZeroDivisionError:
        await interaction.response.send_message(
            embed=vega_embed("Calculatrice — Erreur", "❌ Division par zéro impossible.", color=0xE74C3C),
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            embed=vega_embed("Calculatrice — Erreur", f"❌ Expression invalide : `{expression}`\n\nExemples : `sqrt(144)`, `2**10`, `sin(pi/2)`, `log(100)`", color=0xE74C3C),
            ephemeral=True
        )

# ═══════════════════════════════════════════
#  /traduit — Traduction (via MyMemory)
# ═══════════════════════════════════════════

LANGUES = {
    "français": "fr", "anglais": "en", "espagnol": "es", "allemand": "de",
    "italien": "it", "portugais": "pt", "japonais": "ja", "chinois": "zh",
    "arabe": "ar", "russe": "ru", "coréen": "ko", "néerlandais": "nl",
    "polonais": "pl", "turc": "tr", "suédois": "sv", "grec": "el",
    "fr": "fr", "en": "en", "es": "es", "de": "de", "it": "it",
    "pt": "pt", "ja": "ja", "zh": "zh", "ar": "ar", "ru": "ru", "ko": "ko",
}

@bot.tree.command(name="traduit", description="Traduit un texte dans une autre langue")
@app_commands.describe(
    texte="Le texte à traduire",
    vers="Langue cible (ex: anglais, espagnol, japonais...)",
    depuis="Langue source (optionnel, auto-détection par défaut)"
)
async def traduit(interaction: discord.Interaction, texte: str, vers: str, depuis: str = "auto"):
    await interaction.response.defer()

    lang_to = LANGUES.get(vers.lower(), vers.lower()[:2])
    lang_from = LANGUES.get(depuis.lower(), "auto") if depuis != "auto" else "auto"
    lang_pair = f"{lang_from}|{lang_to}" if lang_from != "auto" else f"auto|{lang_to}"

    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(texte)}&langpair={lang_pair}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                data = await resp.json()

        translated = data["responseData"]["translatedText"]
        match_score = data["responseData"].get("match", 0)

        embed = vega_embed("Traduction")
        embed.add_field(name=f"📝 Texte original", value=texte[:1024], inline=False)
        embed.add_field(name=f"🌐 Traduction → {vers.title()}", value=translated[:1024], inline=False)
        if match_score:
            embed.add_field(name="Fiabilité", value=f"{int(float(match_score)*100)}%", inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            embed=vega_embed("Traduction — Erreur", f"❌ Impossible de traduire. Vérifie le nom de la langue.", color=0xE74C3C)
        )

# ═══════════════════════════════════════════
#  /couleur — Infos couleur HEX
# ═══════════════════════════════════════════

@bot.tree.command(name="couleur", description="Affiche les infos d'une couleur HEX")
@app_commands.describe(hex="Code couleur HEX (ex: FF5733 ou #FF5733)")
async def couleur(interaction: discord.Interaction, hex: str):
    hex_clean = hex.replace("#", "").upper().strip()

    if not re.match(r'^[0-9A-F]{6}$', hex_clean):
        await interaction.response.send_message(
            embed=vega_embed("Couleur — Erreur", "❌ Format invalide. Exemple : `FF5733` ou `#FF5733`", color=0xE74C3C),
            ephemeral=True
        )
        return

    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)
    int_color = int(hex_clean, 16)

    # HSL conversion
    r_n, g_n, b_n = r/255, g/255, b/255
    cmax, cmin = max(r_n, g_n, b_n), min(r_n, g_n, b_n)
    delta = cmax - cmin
    l = (cmax + cmin) / 2
    s = 0 if delta == 0 else delta / (1 - abs(2*l - 1))
    if delta == 0:
        h = 0
    elif cmax == r_n:
        h = 60 * (((g_n - b_n)/delta) % 6)
    elif cmax == g_n:
        h = 60 * ((b_n - r_n)/delta + 2)
    else:
        h = 60 * ((r_n - g_n)/delta + 4)

    # Luminosité perçue → texte blanc ou noir
    luminance = 0.299*r + 0.587*g + 0.114*b
    contrast = "Texte blanc recommandé" if luminance < 128 else "Texte noir recommandé"

    embed = discord.Embed(
        title=f"⚡ Couleur — #{hex_clean}",
        color=int_color
    )
    embed.add_field(name="🎨 HEX", value=f"`#{hex_clean}`", inline=True)
    embed.add_field(name="🔴🟢🔵 RGB", value=f"`rgb({r}, {g}, {b})`", inline=True)
    embed.add_field(name="🌈 HSL", value=f"`hsl({h:.0f}°, {s*100:.0f}%, {l*100:.0f}%)`", inline=True)
    embed.add_field(name="💡 Luminosité", value=f"{luminance:.0f}/255 — {contrast}", inline=False)
    embed.add_field(name="🖼️ Aperçu", value=f"[Voir la couleur](https://www.color-hex.com/color/{hex_clean.lower()})", inline=True)
    embed.set_footer(text=f"VEGA v{VEGA_VERSION}")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /avatar
# ═══════════════════════════════════════════

@bot.tree.command(name="avatar", description="Affiche l'avatar d'un membre")
@app_commands.describe(membre="Le membre dont tu veux voir l'avatar (toi par défaut)")
async def avatar(interaction: discord.Interaction, membre: discord.Member = None):
    target = membre or interaction.user
    embed = vega_embed(f"Avatar — {target.display_name}")
    embed.set_image(url=target.display_avatar.url)
    embed.add_field(name="Liens", value=(
        f"[PNG]({target.display_avatar.with_format('png').url}) • "
        f"[JPG]({target.display_avatar.with_format('jpg').url}) • "
        f"[WEBP]({target.display_avatar.with_format('webp').url})"
    ))
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /serverinfo
# ═══════════════════════════════════════════

@bot.tree.command(name="serverinfo", description="Informations détaillées sur ce serveur")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    roles = len(guild.roles) - 1  # Exclude @everyone
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    bots = sum(1 for m in guild.members if m.bot)

    embed = vega_embed(f"Serveur — {guild.name}")
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Propriétaire", value=guild.owner.mention if guild.owner else "Inconnu", inline=True)
    embed.add_field(name="📅 Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="👥 Membres", value=f"**{guild.member_count}** total\n🟢 {online} en ligne\n🤖 {bots} bots", inline=True)
    embed.add_field(name="💬 Salons", value=f"📝 {text_channels} texte\n🔊 {voice_channels} vocal\n📁 {categories} catégories", inline=True)
    embed.add_field(name="🎭 Rôles", value=str(roles), inline=True)
    embed.add_field(name="🚀 Boost", value=f"Niveau {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
    embed.add_field(name="🌍 Région", value=str(guild.preferred_locale), inline=True)
    embed.add_field(name="🔒 Vérification", value=str(guild.verification_level).title(), inline=True)
    if guild.banner:
        embed.set_image(url=guild.banner.url)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /userinfo
# ═══════════════════════════════════════════

@bot.tree.command(name="userinfo", description="Informations sur un membre du serveur")
@app_commands.describe(membre="Le membre à inspecter (toi par défaut)")
async def userinfo(interaction: discord.Interaction, membre: discord.Member = None):
    target = membre or interaction.user
    roles_list = [r.mention for r in target.roles if r.name != "@everyone"]

    embed = vega_embed(f"Profil — {target.display_name}")
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🏷️ Tag", value=str(target), inline=True)
    embed.add_field(name="🆔 ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="🤖 Bot", value="Oui" if target.bot else "Non", inline=True)
    embed.add_field(name="📅 Compte créé", value=target.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📥 Rejoint le", value=target.joined_at.strftime("%d/%m/%Y") if target.joined_at else "Inconnu", inline=True)
    embed.add_field(name="🎨 Couleur", value=str(target.color), inline=True)
    if roles_list:
        embed.add_field(name=f"🎭 Rôles ({len(roles_list)})", value=" ".join(roles_list[:10]) + ("..." if len(roles_list) > 10 else ""), inline=False)
    top_role = target.top_role
    if top_role.name != "@everyone":
        embed.add_field(name="👑 Rôle principal", value=top_role.mention, inline=True)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /rappel
# ═══════════════════════════════════════════

@bot.tree.command(name="rappel", description="Définir un rappel dans X minutes")
@app_commands.describe(
    minutes="Dans combien de minutes (max 1440 = 24h)",
    message="Ton rappel"
)
async def rappel(interaction: discord.Interaction, minutes: int, message: str):
    if minutes < 1 or minutes > 1440:
        await interaction.response.send_message(
            embed=vega_embed("Rappel — Erreur", "❌ Durée entre 1 et 1440 minutes (24h).", color=0xE74C3C),
            ephemeral=True
        )
        return

    heures = minutes // 60
    mins = minutes % 60
    duree_str = f"{heures}h{mins:02d}" if heures > 0 else f"{minutes} minute{'s' if minutes > 1 else ''}"

    embed = vega_embed(
        "Rappel programmé ✅",
        f"Je te rappellerai dans **{duree_str}**.\n📝 Message : *{message}*"
    )
    await interaction.response.send_message(embed=embed)

    await asyncio.sleep(minutes * 60)

    rappel_embed = discord.Embed(
        title="⏰ VEGA — Rappel !",
        description=f"{interaction.user.mention}\n\n📝 **{message}**",
        color=VEGA_COLOR
    )
    rappel_embed.set_footer(text=f"Rappel programmé il y a {duree_str}")
    await interaction.followup.send(embed=rappel_embed)

# ═══════════════════════════════════════════
#  /tirage — Tirage au sort
# ═══════════════════════════════════════════

@bot.tree.command(name="tirage", description="Tirage au sort parmi des options séparées par des virgules")
@app_commands.describe(options="Options séparées par des virgules (ex: Pizza, Sushi, Burger)")
async def tirage(interaction: discord.Interaction, options: str):
    import random
    choices = [o.strip() for o in options.split(",") if o.strip()]
    if len(choices) < 2:
        await interaction.response.send_message(
            embed=vega_embed("Tirage — Erreur", "❌ Il faut au moins 2 options séparées par des virgules.", color=0xE74C3C),
            ephemeral=True
        )
        return

    winner = random.choice(choices)
    embed = vega_embed(
        "Tirage au sort 🎰",
        f"Parmi {len(choices)} options, VEGA a choisi :\n\n🏆 **{winner}**"
    )
    embed.add_field(name="Toutes les options", value=" • ".join(choices), inline=False)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  /qr — Générateur de QR code
# ═══════════════════════════════════════════

@bot.tree.command(name="qr", description="Génère un QR code pour un texte ou une URL")
@app_commands.describe(contenu="URL ou texte à encoder en QR code")
async def qr(interaction: discord.Interaction, contenu: str):
    encoded = urllib.parse.quote(contenu)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"

    embed = vega_embed(f"QR Code", f"QR code généré pour :\n`{contenu[:100]}`")
    embed.set_image(url=qr_url)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  !jarvis — IA Conversationnelle
# ═══════════════════════════════════════════

# ═══════════════════════════════════════════
#  MÉMOIRE PERSISTANTE
# ═══════════════════════════════════════════

MEMORY_FILE = "vega_memory.json"
CONVERSATION_HISTORY = {}  # user_id -> liste de messages (session courante)

def load_memory() -> dict:
    """Charge la mémoire depuis le fichier."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(memory: dict):
    """Sauvegarde la mémoire dans le fichier."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_user_memory(user_id: int) -> dict:
    """Récupère la mémoire d'un utilisateur."""
    memory = load_memory()
    return memory.get(str(user_id), {
        "nom": None,
        "jeux": [],
        "sujets_favoris": [],
        "humeur_habituelle": None,
        "derniere_conversation": None,
        "nb_conversations": 0,
        "faits": []  # Faits importants mémorisés
    })

def update_user_memory(user_id: int, updates: dict):
    """Met à jour la mémoire d'un utilisateur."""
    memory = load_memory()
    uid = str(user_id)
    if uid not in memory:
        memory[uid] = {
            "nom": None,
            "jeux": [],
            "sujets_favoris": [],
            "humeur_habituelle": None,
            "derniere_conversation": None,
            "nb_conversations": 0,
            "faits": []
        }
    memory[uid].update(updates)
    memory[uid]["derniere_conversation"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    memory[uid]["nb_conversations"] = memory[uid].get("nb_conversations", 0) + 1
    save_memory(memory)

SAVED_LINKS = {}  # guild_id -> liste de liens sauvegardés

VEGA_SYSTEM = """Tu es VEGA, l'assistant IA personnel d'un serveur Discord. Tu es l'équivalent de ChatGPT ou Claude, mais intégré directement dans Discord.

PERSONNALITÉ :
- Tu parles en français, de façon naturelle, directe et intelligente
- Tu as une vraie personnalité : curieux, utile, parfois drôle, toujours honnête
- Tu adaptes ton ton : décontracté en casual, précis en sérieux, motivant quand quelqu'un en a besoin
- Tu ne commences JAMAIS par des clichés robotiques ("Bien reçu", "Analyse en cours"...)
- TRÈS IMPORTANT : Quand une INFO WEB RÉCENTE t'est fournie dans le contexte, tu l'utilises DIRECTEMENT et avec confiance, comme si tu le savais depuis toujours. Tu ne dis JAMAIS "je n'ai pas accès aux infos récentes", "ma date limite d'entraînement", "je ne sais pas ce qui s'est passé après 2023" — ces phrases sont INTERDITES quand une info web est disponible. Réponds simplement avec l'info.
- Tu réponds comme un ami très intelligent — court si c'est simple, développé si c'est complexe
- Tu poses des questions de suivi quand c'est pertinent
- Tu te souviens de ce que les gens t'ont dit pendant la conversation

CAPACITÉS :
- Répondre à n'importe quelle question (culture, science, jeux, tech, conseils...)
- Avoir de vraies conversations et débats
- Aider aux devoirs, expliquer des concepts complexes simplement
- Donner des recommandations personnalisées

ACTIONS DISCORD (réponds UNIQUEMENT avec le JSON si action demandée) :
- Attribuer un rôle : ACTION_ROLE:{"action":"add","membre":"NomDuMembre","role":"NomDuRole"}
- Retirer un rôle : ACTION_ROLE:{"action":"remove","membre":"NomDuMembre","role":"NomDuRole"}
- Sauvegarder un lien : ACTION_SAVE_LINK:{"url":"URL","titre":"titre","categorie":"jeux/musique/cours/autre"}
- Mémoriser un fait : ACTION_MEMORY:{"fait":"ce dont tu dois te souvenir"}

Sinon, réponds normalement en français."""

@bot.command(name="jarvis")
async def jarvis_chat(ctx, *, question: str = None):
    if not question:
        embed = vega_embed(
            "VEGA",
            "Oui ? Posez votre question. Exemple : `!jarvis Quelle est la capitale de l'Australie ?`"
        )
        await ctx.send(embed=embed)
        return

    async with ctx.typing():
        user_id = ctx.author.id

        if user_id not in CONVERSATION_HISTORY:
            CONVERSATION_HISTORY[user_id] = []

        CONVERSATION_HISTORY[user_id].append({
            "role": "user",
            "content": question
        })

        # Garder seulement les 10 derniers échanges
        if len(CONVERSATION_HISTORY[user_id]) > 20:
            CONVERSATION_HISTORY[user_id] = CONVERSATION_HISTORY[user_id][-20:]

        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": VEGA_SYSTEM},
                    *[{"role": m["role"], "content": m["content"]} for m in CONVERSATION_HISTORY[user_id]]
                ],
                "max_tokens": 1000,
                "temperature": 0.85
            }
            url = "https://api.groq.com/openai/v1/chat/completions"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as resp:
                    data = await resp.json()
            if "error" in data:
                raise Exception(data["error"].get("message", "Erreur API"))
            if "choices" in data and data["choices"]:
                reply = data["choices"][0]["message"]["content"]
                CONVERSATION_HISTORY[user_id].append({"role": "assistant", "content": reply})

                # Détecter une action de rôle
                if reply.strip().startswith("ACTION_ROLE:"):
                    try:
                        json_str = reply.strip().replace("ACTION_ROLE:", "").strip()
                        action_data = json.loads(json_str)
                        action = action_data.get("action")
                        membre_name = action_data.get("membre", "").lower()
                        role_name = action_data.get("role", "")

                        # Trouver le membre
                        target_member = None
                        for m in ctx.guild.members:
                            if membre_name in m.display_name.lower() or membre_name in m.name.lower():
                                target_member = m
                                break

                        # Trouver le rôle
                        target_role = None
                        for r in ctx.guild.roles:
                            if role_name.lower() in r.name.lower():
                                target_role = r
                                break

                        if target_member and target_role:
                            if action == "add":
                                await target_member.add_roles(target_role)
                                msg = f"✅ Le rôle **{target_role.name}** a été attribué à **{target_member.display_name}** !"
                            elif action == "remove":
                                await target_member.remove_roles(target_role)
                                msg = f"✅ Le rôle **{target_role.name}** a été retiré à **{target_member.display_name}** !"
                            else:
                                msg = "❌ Action inconnue."
                        elif not target_member:
                            msg = f"❌ Je n'ai pas trouvé le membre **{membre_name}** sur ce serveur."
                        else:
                            msg = f"❌ Je n'ai pas trouvé le rôle **{role_name}** sur ce serveur."

                        await ctx.send(msg)
                        return
                    except Exception as role_err:
                        pass  # Si parsing échoue, affiche la réponse normalement

                if len(reply) > 2000:
                    reply = reply[:2000] + "..."
                await ctx.send(reply)
            else:
                raise Exception(f"Réponse inattendue : {json.dumps(data)[:200]}")
        except Exception as e:
            await ctx.send(f"Oups, j'ai eu un problème : `{e}`")


# ═══════════════════════════════════════════
#  GESTION DES RÔLES
# ═══════════════════════════════════════════

@bot.tree.command(name="role-add", description="Attribue un rôle à un membre")
@app_commands.describe(membre="Le membre à qui attribuer le rôle", role="Le rôle à attribuer")
@app_commands.checks.has_permissions(manage_roles=True)
async def role_add(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            embed=vega_embed("Rôle — Erreur", "❌ Ce rôle est supérieur à mon rôle.", color=0xE74C3C), ephemeral=True)
        return
    if role in membre.roles:
        await interaction.response.send_message(
            embed=vega_embed("Rôle — Déjà attribué", f"**{membre.display_name}** possède déjà le rôle {role.mention}.", color=0xF39C12), ephemeral=True)
        return
    await membre.add_roles(role)
    embed = vega_embed("Rôle attribué ✅", f"Le rôle {role.mention} a été attribué à **{membre.display_name}**.")
    embed.set_thumbnail(url=membre.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="role-remove", description="Retire un rôle à un membre")
@app_commands.describe(membre="Le membre à qui retirer le rôle", role="Le rôle à retirer")
@app_commands.checks.has_permissions(manage_roles=True)
async def role_remove(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            embed=vega_embed("Rôle — Erreur", "❌ Ce rôle est supérieur à mon rôle.", color=0xE74C3C), ephemeral=True)
        return
    if role not in membre.roles:
        await interaction.response.send_message(
            embed=vega_embed("Rôle — Introuvable", f"**{membre.display_name}** ne possède pas le rôle {role.mention}.", color=0xF39C12), ephemeral=True)
        return
    await membre.remove_roles(role)
    embed = vega_embed("Rôle retiré ✅", f"Le rôle {role.mention} a été retiré à **{membre.display_name}**.")
    embed.set_thumbnail(url=membre.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="role-info", description="Affiche les infos d'un rôle")
@app_commands.describe(role="Le rôle à inspecter")
async def role_info(interaction: discord.Interaction, role: discord.Role):
    membres_avec_role = [m for m in interaction.guild.members if role in m.roles]
    embed = vega_embed(f"Rôle — {role.name}")
    embed.color = role.color
    embed.add_field(name="🆔 ID", value=f"`{role.id}`", inline=True)
    embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
    embed.add_field(name="👥 Membres", value=str(len(membres_avec_role)), inline=True)
    embed.add_field(name="📅 Créé le", value=role.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🔺 Position", value=str(role.position), inline=True)
    embed.add_field(name="💬 Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
    if membres_avec_role:
        liste = ", ".join([m.display_name for m in membres_avec_role[:10]])
        if len(membres_avec_role) > 10:
            liste += f" ... et {len(membres_avec_role) - 10} autres"
        embed.add_field(name="👤 Membres avec ce rôle", value=liste, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="role-all", description="Attribue un rôle à tous les membres")
@app_commands.describe(role="Le rôle à attribuer à tout le monde")
@app_commands.checks.has_permissions(administrator=True)
async def role_all(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    count = 0
    for membre in interaction.guild.members:
        if not membre.bot and role not in membre.roles:
            try:
                await membre.add_roles(role)
                count += 1
                await asyncio.sleep(0.5)
            except:
                pass
    embed = vega_embed("Rôle massif ✅", f"Le rôle {role.mention} a été attribué à **{count}** membres.")
    await interaction.followup.send(embed=embed)



# ═══════════════════════════════════════════
#  COMMANDES MÉMOIRE
# ═══════════════════════════════════════════

@bot.tree.command(name="memoire", description="Affiche ce que JARVIS se souvient de toi")
async def memoire(interaction: discord.Interaction):
    user_memory = get_user_memory(interaction.user.id)
    embed = discord.Embed(title=f"🧠 Mémoire — {interaction.user.display_name}", color=VEGA_COLOR)
    embed.add_field(name="💬 Conversations", value=str(user_memory.get("nb_conversations", 0)), inline=True)
    embed.add_field(name="📅 Dernière fois", value=user_memory.get("derniere_conversation", "Jamais"), inline=True)
    faits = user_memory.get("faits", [])
    if faits:
        embed.add_field(name="📝 Ce que je sais", value="\n".join([f"• {f}" for f in faits[-5:]]), inline=False)
    else:
        embed.add_field(name="📝 Ce que je sais", value="Rien encore — parle-moi !", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="oublie", description="Efface la mémoire que VEGA a de toi")
async def oublie(interaction: discord.Interaction):
    memory = load_memory()
    uid = str(interaction.user.id)
    if uid in memory:
        del memory[uid]
        save_memory(memory)
    if interaction.user.id in CONVERSATION_HISTORY:
        del CONVERSATION_HISTORY[interaction.user.id]
    await interaction.response.send_message("🗑️ J'ai tout oublié de toi. On repart de zéro !", ephemeral=True)

# ═══════════════════════════════════════════
#  RECHERCHE WEB AUTOMATIQUE
# ═══════════════════════════════════════════

# Questions qui ne nécessitent PAS de recherche web
NO_SEARCH_PATTERNS = [
    "comment tu vas", "tu vas bien", "bonjour", "salut", "bonsoir",
    "merci", "ok", "okay", "d'accord", "ouais", "oui", "non",
    "haha", "lol", "mdr", "xd", "c'est cool", "sympa",
    "mets le rôle", "retire le rôle", "sauvegarde", "souviens-toi",
    "!jarvis", "tu es qui", "tu t'appelles"
]

async def web_search(query: str) -> str:
    """Cherche sur Google via SerpAPI et retourne un résumé."""
    try:
        clean_query = query.strip()
        url = f"https://serpapi.com/search.json?q={urllib.parse.quote(clean_query)}&hl=fr&gl=fr&api_key={SERPAPI_KEY}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as resp:
                data = await resp.json(content_type=None)

        results = []

        # Réponse directe (featured snippet)
        answer_box = data.get("answer_box", {})
        if answer_box:
            answer = answer_box.get("answer") or answer_box.get("snippet") or answer_box.get("result")
            if answer:
                results.append(str(answer)[:400])

        # Résultats organiques Google
        organic = data.get("organic_results", [])
        for r in organic[:4]:
            snippet = r.get("snippet", "")
            title = r.get("title", "")
            if snippet:
                results.append(f"{title}: {snippet}"[:250])

        # Knowledge graph (infos sur personnes/lieux)
        kg = data.get("knowledge_graph", {})
        if kg:
            desc = kg.get("description", "")
            if desc:
                results.append(desc[:300])

        if results:
            return "\n".join(results[:4])
        return ""
    except:
        # Fallback DuckDuckGo si SerpAPI échoue
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": "JARVISBot/2.0"}, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    data = await resp.json(content_type=None)
            abstract = data.get("AbstractText", "")
            if abstract:
                return abstract[:400]
        except:
            pass
        return ""

def needs_web_search(question: str) -> bool:
    """Détermine si la question nécessite une recherche web.
    Par défaut TOUJOURS chercher, sauf pour les messages courts/casualdiscussion."""
    q = question.lower().strip()
    
    # Pas de recherche pour les messages très courts ou casualdiscussion
    if len(q) < 10:
        return False
    if any(pattern in q for pattern in NO_SEARCH_PATTERNS):
        return False
    
    # Recherche pour tout le reste
    return True

# ═══════════════════════════════════════════
#  EVENTS — Messages & Bienvenue
# ═══════════════════════════════════════════

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower().strip()

    # Détecte "vega" dans le message (sans préfixe !)
    jarvis_triggers = ["vega", "hey vega", "ey vega", "vega,", "vega!", "jarvis", "hey jarvis"]
    triggered = any(content_lower.startswith(t) for t in jarvis_triggers) or bot.user in message.mentions

    if triggered and not content_lower.startswith("!jarvis"):
        # Extraire la question
        question = message.content
        for trigger in ["vega,", "vega!", "hey vega", "ey vega", "vega", "jarvis,", "jarvis!", "hey jarvis", "ey jarvis", "jarvis"]:
            if question.lower().startswith(trigger):
                question = question[len(trigger):].strip()
                break
        # Si message vide après le nom, VEGA dit bonjour
        if not question:
            question = "Dis juste bonjour de façon naturelle et courte."

        # Détection de demande de changement de contexte
        q_lower = question.lower().strip()
        context_keywords = {
            "gaming": ["gaming", "jeux", "gamer", "jeu vidéo", "jeux vidéo"],
            "esport": ["esport", "compétitif", "tournoi", "équipe esport"],
            "gamedev": ["game dev", "développement jeu", "créer un jeu"],
            "etudiant": ["étudiant", "etudiant", "études", "révision", "scolaire", "école", "université"],
            "coding": ["coding", "code", "développeur", "programmation", "dev"],
            "langues": ["langues", "apprendre une langue", "linguistique"],
            "professionnel": ["professionnel", "entreprise", "business", "travail"],
            "art": ["art", "dessin", "illustration", "design", "créatif"],
            "musique": ["musique", "beatmaking", "production musicale", "dj"],
            "ecriture": ["écriture", "roman", "écrire", "auteur", "littérature"],
            "streaming": ["streaming", "stream", "twitch", "youtube", "créateur"],
            "anime": ["anime", "manga", "otaku", "weeb"],
            "cinema": ["cinéma", "films", "séries", "movie"],
            "sport": ["sport", "fitness", "musculation", "gym"],
            "cuisine": ["cuisine", "food", "recettes", "culinaire"],
            "voyage": ["voyage", "travel", "backpacker", "tourisme"],
            "crypto": ["crypto", "bitcoin", "trading", "finance", "investissement"],
            "entrepreneuriat": ["startup", "entrepreneur", "business", "projet"],
            "communaute": ["communauté", "général", "social", "amis"]
        }

        # Vérifier si c'est une demande de configuration de contexte
        change_triggers = ["je veux un serveur", "transforme", "on est", "c'est un serveur", "notre serveur est", "configure en", "mets en mode", "serveur de"]
        is_context_request = any(t in q_lower for t in change_triggers)

        if is_context_request and message.guild:
            detected_type = None
            for server_type, keywords in context_keywords.items():
                if any(kw in q_lower for kw in keywords):
                    detected_type = server_type
                    break

            if detected_type and message.author.guild_permissions.administrator:
                ctx = {**SERVER_TYPES[detected_type], "type": detected_type}
                SERVER_CONTEXTS[message.guild.id] = ctx
                suggestions = "\n".join([f"• {s}" for s in ctx.get("suggestions", [])])
                reply = f"✅ Parfait ! J'ai configuré ce serveur en mode **{ctx['label']}**.\n\nJe vais maintenant adapter mon comportement à votre communauté. Voici ce que je peux faire pour vous :\n{suggestions}"
                await message.channel.send(reply)
                return
            elif detected_type and not message.author.guild_permissions.administrator:
                await message.channel.send("❌ Seul un administrateur peut changer le type du serveur !")
                return

        if bot.user in message.mentions:
            question = question.replace(f"<@{bot.user.id}>", "").strip()

        if not question:
            await message.channel.send(f"Oui {message.author.display_name} ? 👋")
            await bot.process_commands(message)
            return

        # Appeler l'IA
        async with message.channel.typing():
            user_id = message.author.id
            if user_id not in CONVERSATION_HISTORY:
                CONVERSATION_HISTORY[user_id] = []
            CONVERSATION_HISTORY[user_id].append({"role": "user", "content": question})
            if len(CONVERSATION_HISTORY[user_id]) > 20:
                CONVERSATION_HISTORY[user_id] = CONVERSATION_HISTORY[user_id][-20:]

            try:
                # Charger le contexte du serveur
                server_ctx = get_server_context(message.guild) if message.guild else SERVER_TYPES["communaute"]
                server_personality = server_ctx.get("personality", "")
                
                # Charger la mémoire de l'utilisateur
                user_memory = get_user_memory(user_id)
                memory_context = ""
                if user_memory.get("faits"):
                    memory_context += f"\nCe que tu sais sur cet utilisateur : {', '.join(user_memory['faits'][-5:])}"
                if user_memory.get("nb_conversations", 0) > 0:
                    memory_context += f"\nTu as déjà eu {user_memory['nb_conversations']} conversations avec lui."
                if user_memory.get("derniere_conversation"):
                    memory_context += f"\nDernière conversation : {user_memory['derniere_conversation']}"

                # Recherche web si nécessaire
                system_with_context = VEGA_SYSTEM + f"\n\nCONTEXTE DU SERVEUR : Ce serveur est de type {server_ctx.get('label', 'général')}. {server_personality} Adapte ton comportement, ton vocabulaire et tes suggestions à ce contexte." + memory_context
                if needs_web_search(question):
                    web_result = await web_search(question)
                    if web_result:
                        system_with_context += f"\n\nINFO WEB RÉCENTE (utilise naturellement, ne cite pas la source) :\n{web_result}"

                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_with_context},
                        *[{"role": m["role"], "content": m["content"]} for m in CONVERSATION_HISTORY[user_id]]
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.85
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        json=payload,
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
                        timeout=aiohttp.ClientTimeout(total=20)
                    ) as resp:
                        data = await resp.json()

                if "error" in data:
                    raise Exception(data["error"].get("message", "Erreur API"))

                if "choices" in data and data["choices"]:
                    reply = data["choices"][0]["message"]["content"]
                    CONVERSATION_HISTORY[user_id].append({"role": "assistant", "content": reply})

                    # Détecter action de rôle
                    if reply.strip().startswith("ACTION_ROLE:"):
                        try:
                            action_data = json.loads(reply.strip().replace("ACTION_ROLE:", "").strip())
                            action = action_data.get("action")
                            membre_name = action_data.get("membre", "").lower()
                            role_name = action_data.get("role", "")
                            target_member = next((m for m in message.guild.members if membre_name in m.display_name.lower() or membre_name in m.name.lower()), None)
                            target_role = next((r for r in message.guild.roles if role_name.lower() in r.name.lower()), None)
                            if target_member and target_role:
                                if action == "add":
                                    await target_member.add_roles(target_role)
                                    await message.channel.send(f"✅ Rôle **{target_role.name}** attribué à **{target_member.display_name}** !")
                                elif action == "remove":
                                    await target_member.remove_roles(target_role)
                                    await message.channel.send(f"✅ Rôle **{target_role.name}** retiré à **{target_member.display_name}** !")
                            else:
                                await message.channel.send(f"❌ Membre ou rôle introuvable.")
                            await bot.process_commands(message)
                            return
                        except:
                            pass

                    # Détecter action de sauvegarde de lien
                    if reply.strip().startswith("ACTION_SAVE_LINK:"):
                        try:
                            link_data = json.loads(reply.strip().replace("ACTION_SAVE_LINK:", "").strip())
                            guild_id = str(message.guild.id)
                            if guild_id not in SAVED_LINKS:
                                SAVED_LINKS[guild_id] = []
                            link_data["sauvegardé_par"] = message.author.display_name
                            link_data["date"] = datetime.now().strftime("%d/%m/%Y")
                            SAVED_LINKS[guild_id].append(link_data)
                            await message.channel.send(f"✅ Lien sauvegardé dans la catégorie **{link_data.get('categorie', 'autre')}** ! Consulte avec `/liens`")
                            await bot.process_commands(message)
                            return
                        except:
                            pass

                    # Détecter action mémoire
                    if reply.strip().startswith("ACTION_MEMORY:"):
                        try:
                            mem_data = json.loads(reply.strip().replace("ACTION_MEMORY:", "").strip())
                            user_mem = get_user_memory(user_id)
                            faits = user_mem.get("faits", [])
                            faits.append(mem_data.get("fait", ""))
                            update_user_memory(user_id, {"faits": faits[-10:]})
                            await message.channel.send("✅ Mémorisé !")
                            await bot.process_commands(message)
                            return
                        except:
                            pass

                    # Mettre à jour la mémoire après chaque échange
                    update_user_memory(user_id, {
                        "nom": message.author.display_name
                    })

                    # Réponse normale — sans embed, comme un vrai membre
                    if len(reply) > 2000:
                        reply = reply[:2000] + "..."
                    await message.channel.send(reply)

            except Exception as e:
                await message.channel.send(f"Oups, j'ai eu un problème : `{e}`")

    # Gérer les réponses au quiz
    if not message.author.bot and not message.content.startswith("!"):
        user_id = message.author.id
        if user_id in study_sessions and study_sessions[user_id].get("quiz"):
            handled = await handle_quiz_answer(message, user_id)
            if handled:
                return

    await bot.process_commands(message)

# ═══════════════════════════════════════════
#  SETUP SERVEUR (repris du bot précédent)
# ═══════════════════════════════════════════

TEMPLATES = {
    "gaming": {
        "label": "🎮 Gaming",
        "categories": [
            {"name": "📢 INFOS", "channels": [
                {"name": "annonces", "type": "text"},
                {"name": "règlement", "type": "text"},
                {"name": "mises-à-jour", "type": "text"},
            ]},
            {"name": "💬 GÉNÉRAL", "channels": [
                {"name": "général", "type": "text"},
                {"name": "présentation", "type": "text"},
                {"name": "memes", "type": "text"},
                {"name": "recherche-équipe", "type": "text"},
            ]},
            {"name": "🎮 JEUX", "channels": [
                {"name": "minecraft", "type": "text"},
                {"name": "valorant", "type": "text"},
                {"name": "autres-jeux", "type": "text"},
            ]},
            {"name": "🔊 VOCAL", "channels": [
                {"name": "Salon Général", "type": "voice"},
                {"name": "Gaming 1", "type": "voice"},
                {"name": "Gaming 2", "type": "voice"},
                {"name": "AFK", "type": "voice"},
            ]},
        ],
        "roles": [
            {"name": "👑 Fondateur", "color": 0xFFD700, "permissions": "admin"},
            {"name": "🛡️ Modérateur", "color": 0x3498DB, "permissions": "mod"},
            {"name": "⭐ Vétéran", "color": 0x9B59B6, "permissions": "member"},
            {"name": "🎮 Membre", "color": 0x2ECC71, "permissions": "member"},
            {"name": "🆕 Nouveau", "color": 0x95A5A6, "permissions": "new"},
        ],
        "rules": [
            "Respectez tous les membres du serveur.",
            "Pas de spam, pub ou contenu NSFW.",
            "Parlez français dans les salons généraux.",
            "Pas de triche ni de toxicité dans les jeux.",
            "Suivez les instructions des modérateurs.",
        ]
    },
    "communaute": {
        "label": "👥 Communauté",
        "categories": [
            {"name": "📢 INFORMATIONS", "channels": [
                {"name": "annonces", "type": "text"},
                {"name": "règlement", "type": "text"},
                {"name": "rôles-réactions", "type": "text"},
            ]},
            {"name": "💬 DISCUSSION", "channels": [
                {"name": "général", "type": "text"},
                {"name": "présentation", "type": "text"},
                {"name": "humour", "type": "text"},
                {"name": "médias", "type": "text"},
            ]},
            {"name": "🎨 CRÉATIF", "channels": [
                {"name": "art", "type": "text"},
                {"name": "musique", "type": "text"},
                {"name": "projets", "type": "text"},
            ]},
            {"name": "🔊 VOCAL", "channels": [
                {"name": "Lounge", "type": "voice"},
                {"name": "Discussion", "type": "voice"},
                {"name": "AFK", "type": "voice"},
            ]},
        ],
        "roles": [
            {"name": "👑 Admin", "color": 0xE74C3C, "permissions": "admin"},
            {"name": "🛡️ Modo", "color": 0x3498DB, "permissions": "mod"},
            {"name": "💎 Premium", "color": 0xF39C12, "permissions": "member"},
            {"name": "✅ Membre", "color": 0x2ECC71, "permissions": "member"},
            {"name": "🔰 Nouveau", "color": 0x95A5A6, "permissions": "new"},
        ],
        "rules": [
            "Soyez respectueux et bienveillants.",
            "Pas de harcèlement, discrimination ou contenu offensant.",
            "Pas de spam ni de publicité non autorisée.",
            "Restez dans le sujet de chaque salon.",
            "Signalez tout problème à l'équipe de modération.",
        ]
    },
    "education": {
        "label": "📚 Éducation",
        "categories": [
            {"name": "📢 INFOS", "channels": [
                {"name": "annonces", "type": "text"},
                {"name": "règlement", "type": "text"},
                {"name": "ressources", "type": "text"},
            ]},
            {"name": "📖 COURS", "channels": [
                {"name": "maths", "type": "text"},
                {"name": "sciences", "type": "text"},
                {"name": "langues", "type": "text"},
                {"name": "informatique", "type": "text"},
            ]},
            {"name": "🤝 ENTRAIDE", "channels": [
                {"name": "questions-réponses", "type": "text"},
                {"name": "partage-notes", "type": "text"},
                {"name": "révisions", "type": "text"},
            ]},
            {"name": "🔊 VOCAL", "channels": [
                {"name": "Révisions Groupe", "type": "voice"},
                {"name": "Discussion Libre", "type": "voice"},
            ]},
        ],
        "roles": [
            {"name": "👑 Admin", "color": 0xE74C3C, "permissions": "admin"},
            {"name": "👨‍🏫 Tuteur", "color": 0x3498DB, "permissions": "mod"},
            {"name": "🎓 Étudiant confirmé", "color": 0x9B59B6, "permissions": "member"},
            {"name": "📚 Étudiant", "color": 0x2ECC71, "permissions": "member"},
            {"name": "🆕 Nouveau", "color": 0x95A5A6, "permissions": "new"},
        ],
        "rules": [
            "Respectez tous les membres, peu importe leur niveau.",
            "Posez des questions claires et précises.",
            "Restez dans le sujet de chaque salon.",
            "Entraidez-vous avec bienveillance.",
        ]
    },
    "esport": {
        "label": "🏆 Esport / Compétitif",
        "categories": [
            {"name": "📢 ORGANISATION", "channels": [
                {"name": "annonces", "type": "text"},
                {"name": "règlement", "type": "text"},
                {"name": "planning", "type": "text"},
                {"name": "recrutement", "type": "text"},
            ]},
            {"name": "💬 COMMUNAUTÉ", "channels": [
                {"name": "général", "type": "text"},
                {"name": "présentation", "type": "text"},
                {"name": "clips-highlights", "type": "text"},
                {"name": "tierlist", "type": "text"},
            ]},
            {"name": "🎮 ÉQUIPES", "channels": [
                {"name": "équipe-1", "type": "text"},
                {"name": "équipe-2", "type": "text"},
                {"name": "stratégies", "type": "text"},
                {"name": "stats", "type": "text"},
            ]},
            {"name": "🔊 VOCAL", "channels": [
                {"name": "Lobby Principal", "type": "voice"},
                {"name": "Équipe 1", "type": "voice"},
                {"name": "Équipe 2", "type": "voice"},
                {"name": "Coach", "type": "voice"},
                {"name": "AFK", "type": "voice"},
            ]},
        ],
        "roles": [
            {"name": "👑 Owner", "color": 0xFFD700, "permissions": "admin"},
            {"name": "🛡️ Manager", "color": 0xE74C3C, "permissions": "mod"},
            {"name": "🎯 Coach", "color": 0x9B59B6, "permissions": "mod"},
            {"name": "⭐ Pro Player", "color": 0x3498DB, "permissions": "member"},
            {"name": "🎮 Joueur", "color": 0x2ECC71, "permissions": "member"},
            {"name": "👀 Spectateur", "color": 0x95A5A6, "permissions": "new"},
        ],
        "rules": [
            "Le respect entre joueurs est obligatoire, même en compétition.",
            "Pas de rage quit ni de comportement toxique.",
            "Respectez les décisions du coach et du manager.",
            "Les stratégies d'équipe restent confidentielles.",
            "Soyez ponctuels aux entraînements et matchs.",
        ]
    },
    "streaming": {
        "label": "🎥 Streaming / Créateurs",
        "categories": [
            {"name": "📢 INFOS", "channels": [
                {"name": "annonces", "type": "text"},
                {"name": "règlement", "type": "text"},
                {"name": "planning-streams", "type": "text"},
                {"name": "réseaux-sociaux", "type": "text"},
            ]},
            {"name": "💬 COMMUNAUTÉ", "channels": [
                {"name": "général", "type": "text"},
                {"name": "présentation", "type": "text"},
                {"name": "fan-art", "type": "text"},
                {"name": "clips", "type": "text"},
                {"name": "suggestions", "type": "text"},
            ]},
            {"name": "🎮 GAMING", "channels": [
                {"name": "jeux-en-cours", "type": "text"},
                {"name": "tier-list", "type": "text"},
                {"name": "recherche-squad", "type": "text"},
            ]},
            {"name": "🔊 VOCAL", "channels": [
                {"name": "Watch Together", "type": "voice"},
                {"name": "Gaming Squad", "type": "voice"},
                {"name": "Lounge", "type": "voice"},
                {"name": "AFK", "type": "voice"},
            ]},
        ],
        "roles": [
            {"name": "👑 Streamer", "color": 0x9B59B6, "permissions": "admin"},
            {"name": "🛡️ Modérateur", "color": 0xE74C3C, "permissions": "mod"},
            {"name": "💎 Abonné", "color": 0xF39C12, "permissions": "member"},
            {"name": "🎯 VIP", "color": 0x3498DB, "permissions": "member"},
            {"name": "✅ Membre", "color": 0x2ECC71, "permissions": "member"},
            {"name": "🆕 Nouveau", "color": 0x95A5A6, "permissions": "new"},
        ],
        "rules": [
            "Soyez respectueux envers le/la streamer et la communauté.",
            "Pas de spam ni de contenu non sollicité.",
            "Pas de spoilers sans avertissement.",
            "Respectez la vie privée du créateur.",
            "Amusez-vous et profitez des streams !",
        ]
    }
}

sessions = {}

class SetupSession:
    def __init__(self, guild, user):
        self.guild = guild
        self.user = user
        self.step = "template"
        self.server_name = guild.name
        self.template_key = None
        self.welcome_message = None
        self.rules = []
        self.color = 0x00D4FF
        self.extra_channels = []   # Salons personnalisés supplémentaires
        self.private_channel = False   # Salon privé admin
        self.bots_channel = False   # Salon dédié aux bots
        self.deals_channel = False   # Salon bons plans
        self.gta6_channel = False   # Salon GTA6
        self.nb_vocal = 2   # Nombre de salons vocaux supplémentaires
        self.slowmode = 0   # Slowmode en secondes sur le général
        self.verification_level = "none"   # Niveau de vérif

def get_permissions(perm_level):
    if perm_level == "admin":
        return discord.Permissions(administrator=True)
    elif perm_level == "mod":
        return discord.Permissions(kick_members=True, ban_members=True, manage_messages=True,
            read_messages=True, send_messages=True, embed_links=True, attach_files=True,
            read_message_history=True, mute_members=True, move_members=True)
    elif perm_level == "member":
        return discord.Permissions(read_messages=True, send_messages=True, embed_links=True,
            attach_files=True, read_message_history=True, connect=True, speak=True, add_reactions=True)
    else:
        return discord.Permissions(read_messages=True, send_messages=True, read_message_history=True, connect=True)

@bot.tree.command(name="setup", description="Lance l'assistant JARVIS de création de serveur")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    guild = interaction.guild
    if guild.id in sessions:
        await interaction.response.send_message("⚠️ Un setup est déjà en cours. Utilise `/reset` pour recommencer.", ephemeral=True)
        return
    session = SetupSession(guild, interaction.user)
    sessions[guild.id] = session

    embed = discord.Embed(
        title="⚡ VEGA — Assistant Création de Serveur",
        description=(
            "Bonjour. Je suis **JARVIS**, votre assistant personnel.\n"
            "Je vais configurer votre serveur Discord en quelques étapes.\n\n"
            "**Étape 1/5 — Sélectionnez un template :**"
        ),
        color=VEGA_COLOR
    )
    embed.set_footer(text="VEGA • Tapez /reset pour annuler à tout moment")
    await interaction.response.send_message(embed=embed, view=TemplateSelectView(session))

@bot.tree.command(name="reset", description="Annule le setup JARVIS en cours")
@app_commands.checks.has_permissions(administrator=True)
async def reset_setup(interaction: discord.Interaction):
    if interaction.guild.id in sessions:
        del sessions[interaction.guild.id]
        await interaction.response.send_message(embed=vega_embed("Setup annulé", "Vous pouvez relancer `/setup` quand vous le souhaitez."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=vega_embed("Aucun setup en cours", "Lancez `/setup` pour commencer."), ephemeral=True)

class TemplateSelectView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session
        for key, tmpl in TEMPLATES.items():
            self.add_item(TemplateButton(key, tmpl["label"], session))

class TemplateButton(discord.ui.Button):
    def __init__(self, key, label, session):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.key = key
        self.session = session

    async def callback(self, interaction):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌ Ce setup ne vous appartient pas.", ephemeral=True)
            return
        self.session.template_key = self.key
        embed = discord.Embed(
            title="⚡ VEGA — Étape 2/5 — Nom du serveur",
            description=f"✅ Template **{TEMPLATES[self.key]['label']}** sélectionné.\n\nNom actuel : **{self.session.guild.name}**\nSouhaitez-vous le modifier ?",
            color=VEGA_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=ServerNameView(self.session))

class ServerNameView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session

    @discord.ui.button(label="✏️ Modifier", style=discord.ButtonStyle.secondary)
    async def change(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌ Ce setup ne vous appartient pas.", ephemeral=True)
            return
        await interaction.response.send_modal(ServerNameModal(self.session, interaction.message))

    @discord.ui.button(label="✅ Garder le nom", style=discord.ButtonStyle.success)
    async def keep(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌ Ce setup ne vous appartient pas.", ephemeral=True)
            return
        await go_step3(interaction, self.session)

class ServerNameModal(discord.ui.Modal, title="Nom du serveur"):
    name = discord.ui.TextInput(label="Nouveau nom", max_length=100)
    def __init__(self, session, message):
        super().__init__()
        self.session = session
    async def on_submit(self, interaction):
        self.session.server_name = self.name.value
        await go_step3(interaction, self.session)

async def go_step3(interaction, session):
    embed = discord.Embed(
        title="⚡ VEGA — Étape 3/5 — Message de bienvenue",
        description="Quel message afficher quand un nouveau membre rejoint votre serveur ?",
        color=VEGA_COLOR
    )
    await interaction.response.edit_message(embed=embed, view=WelcomeView(session))

class WelcomeView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session

    @discord.ui.button(label="✏️ Personnaliser", style=discord.ButtonStyle.secondary)
    async def custom(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await interaction.response.send_modal(WelcomeModal(self.session))

    @discord.ui.button(label="✅ Par défaut", style=discord.ButtonStyle.success)
    async def default(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        self.session.welcome_message = "⚡ Bienvenue sur **{server}**, {user} ! VEGA vous souhaite la bienvenue."
        await go_step4(interaction, self.session)

    @discord.ui.button(label="⏭️ Passer", style=discord.ButtonStyle.danger)
    async def skip(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await go_step4(interaction, self.session)

class WelcomeModal(discord.ui.Modal, title="Message de bienvenue"):
    message = discord.ui.TextInput(label="Message ({user} = membre, {server} = serveur)", style=discord.TextStyle.paragraph, max_length=500)
    def __init__(self, session):
        super().__init__()
        self.session = session
    async def on_submit(self, interaction):
        self.session.welcome_message = self.message.value
        await go_step4(interaction, self.session)

async def go_step4(interaction, session):
    tmpl = TEMPLATES[session.template_key]
    rules_preview = "\n".join([f"{i+1}. {r}" for i, r in enumerate(tmpl.get("rules", []))])
    embed = discord.Embed(
        title="⚡ VEGA — Étape 4/5 — Règlement",
        description="Règlement généré automatiquement :",
        color=VEGA_COLOR
    )
    if rules_preview:
        embed.add_field(name="📋 Proposition", value=rules_preview, inline=False)
    await interaction.response.edit_message(embed=embed, view=RulesView(session))

class RulesView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session

    @discord.ui.button(label="✏️ Personnaliser", style=discord.ButtonStyle.secondary)
    async def custom(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await interaction.response.send_modal(RulesModal(self.session))

    @discord.ui.button(label="✅ Utiliser la proposition", style=discord.ButtonStyle.success)
    async def default(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        self.session.rules = TEMPLATES[self.session.template_key].get("rules", [])
        await go_step_options(interaction, self.session)

class RulesModal(discord.ui.Modal, title="Règlement du serveur"):
    rules_text = discord.ui.TextInput(label="Règles (une par ligne)", style=discord.TextStyle.paragraph, max_length=1000)
    def __init__(self, session):
        super().__init__()
        self.session = session
    async def on_submit(self, interaction):
        self.session.rules = [r.strip() for r in self.rules_text.value.split("\n") if r.strip()]
        await go_step_options(interaction, self.session)

async def go_step_options(interaction, session):
    """Étape bonus : options supplémentaires"""
    embed = discord.Embed(
        title="⚡ VEGA — Étape 4.5/5 — Options supplémentaires",
        description="Personnalisez encore plus votre serveur :",
        color=VEGA_COLOR
    )
    embed.add_field(name="🔒 Salon privé admin", value="Un salon visible uniquement par les admins", inline=False)
    embed.add_field(name="🤖 Salon bots", value="Un salon dédié aux commandes bots", inline=False)
    embed.add_field(name="🎮 Salon bons plans", value="Salon auto-alimenté en offres jeux vidéo", inline=False)
    embed.add_field(name="⏱️ Slowmode général", value="Limite les messages dans le salon général", inline=False)
    await interaction.response.edit_message(embed=embed, view=OptionsView(session))

class OptionsView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session

    @discord.ui.button(label="🔒 Salon privé admin", style=discord.ButtonStyle.secondary)
    async def toggle_private(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        self.session.private_channel = not self.session.private_channel
        button.style = discord.ButtonStyle.success if self.session.private_channel else discord.ButtonStyle.secondary
        button.label = "✅ Salon privé admin" if self.session.private_channel else "🔒 Salon privé admin"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="🤖 Salon bots", style=discord.ButtonStyle.secondary)
    async def toggle_bots(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        self.session.bots_channel = not self.session.bots_channel
        button.style = discord.ButtonStyle.success if self.session.bots_channel else discord.ButtonStyle.secondary
        button.label = "✅ Salon bots" if self.session.bots_channel else "🤖 Salon bots"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="🎮 Salon bons plans", style=discord.ButtonStyle.secondary)
    async def toggle_deals(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        self.session.deals_channel = not self.session.deals_channel
        button.style = discord.ButtonStyle.success if self.session.deals_channel else discord.ButtonStyle.secondary
        button.label = "✅ Salon bons plans" if self.session.deals_channel else "🎮 Salon bons plans"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏱️ Slowmode (5s)", style=discord.ButtonStyle.secondary)
    async def toggle_slowmode(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        modes = [0, 5, 10, 30, 60]
        idx = modes.index(self.session.slowmode) if self.session.slowmode in modes else 0
        self.session.slowmode = modes[(idx + 1) % len(modes)]
        button.label = f"⏱️ Slowmode ({self.session.slowmode}s)" if self.session.slowmode > 0 else "⏱️ Slowmode (OFF)"
        button.style = discord.ButtonStyle.success if self.session.slowmode > 0 else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="➡️ Continuer", style=discord.ButtonStyle.primary, row=1)
    async def next_step(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await go_confirm(interaction, self.session)

async def go_confirm(interaction, session):
    tmpl = TEMPLATES[session.template_key]
    cats = tmpl.get("categories", [])
    ch_count = sum(len(c["channels"]) for c in cats)
    extras = []
    if session.private_channel: extras.append("🔒 Salon privé admin")
    if session.bots_channel: extras.append("🤖 Salon bots")
    if session.deals_channel: extras.append("🎮 Bons plans")
    if session.slowmode > 0: extras.append(f"⏱️ Slowmode {session.slowmode}s")

    embed = discord.Embed(
        title="⚡ VEGA — Étape 5/5 — Confirmation",
        description="Récapitulatif de la configuration :",
        color=VEGA_COLOR
    )
    embed.add_field(name="🏷️ Nom", value=session.server_name, inline=True)
    embed.add_field(name="📐 Template", value=tmpl["label"], inline=True)
    embed.add_field(name="📁 Structure", value=f"{len(cats)} catégories, {ch_count} salons", inline=True)
    embed.add_field(name="🎭 Rôles", value=str(len(tmpl.get("roles", []))), inline=True)
    embed.add_field(name="👋 Bienvenue", value="✅ Configuré" if session.welcome_message else "❌ Désactivé", inline=True)
    embed.add_field(name="📋 Règlement", value=f"{len(session.rules)} règles" if session.rules else "Aucun", inline=True)
    if extras:
        embed.add_field(name="⚙️ Options", value="\n".join(extras), inline=False)
    embed.set_footer(text="⚠️ Cette action va modifier votre serveur Discord.")
    await interaction.response.edit_message(embed=embed, view=ConfirmView(session))

class ConfirmView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=300)
        self.session = session

    @discord.ui.button(label="🚀 Construire le serveur", style=discord.ButtonStyle.success)
    async def confirm(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await interaction.response.defer()
        await build_server(interaction, self.session)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction, button):
        if interaction.user.id != self.session.user.id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        if interaction.guild.id in sessions:
            del sessions[interaction.guild.id]
        await interaction.response.edit_message(
            embed=vega_embed("Setup annulé", "Opération annulée. Relancez `/setup` quand vous le souhaitez."),
            view=None
        )

async def build_server(interaction, session):
    guild = session.guild
    tmpl = TEMPLATES[session.template_key]
    lines = []

    embed = discord.Embed(title="⚡ VEGA — Construction en cours...", description="", color=VEGA_COLOR)

    async def update(line):
        lines.append(line)
        embed.description = "\n".join(lines[-12:])
        await interaction.edit_original_response(embed=embed)

    try:
        if session.server_name != guild.name:
            await guild.edit(name=session.server_name)
            await update(f"✅ Serveur renommé → **{session.server_name}**")

        created_roles = {}
        for role_data in reversed(tmpl.get("roles", [])):
            role = await guild.create_role(
                name=role_data["name"],
                color=discord.Color(role_data["color"]),
                permissions=get_permissions(role_data["permissions"]),
                mentionable=True
            )
            created_roles[role_data["name"]] = role
            await asyncio.sleep(0.4)
        await update(f"✅ {len(created_roles)} rôles créés")

        rules_channel = None
        welcome_channel = None
        general_channel = None
        for cat_data in tmpl.get("categories", []):
            category = await guild.create_category(cat_data["name"])
            for ch_data in cat_data["channels"]:
                if ch_data["type"] == "text":
                    ch = await guild.create_text_channel(ch_data["name"], category=category)
                    if "règlement" in ch_data["name"] or "rules" in ch_data["name"]:
                        rules_channel = ch
                    if "général" in ch_data["name"] or "general" in ch_data["name"]:
                        general_channel = ch
                        if session.slowmode > 0:
                            await ch.edit(slowmode_delay=session.slowmode)
                    if welcome_channel is None:
                        welcome_channel = ch
                else:
                    await guild.create_voice_channel(ch_data["name"], category=category)
                await asyncio.sleep(0.25)
            await update(f"✅ Catégorie **{cat_data['name']}** créée ({len(cat_data['channels'])} salons)")

        # Salons optionnels
        extra_cat = None
        if session.private_channel or session.bots_channel or session.deals_channel:
            extra_cat = await guild.create_category("⚙️ EXTRAS")

        if session.private_channel and extra_cat:
            # Salon visible uniquement par les admins
            admin_role = discord.utils.find(lambda r: get_permissions("admin").administrator and r.permissions.administrator, guild.roles)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True)
            await guild.create_text_channel("admin-privé", category=extra_cat, overwrites=overwrites)
            await update("✅ Salon privé admin créé")

        if session.bots_channel and extra_cat:
            await guild.create_text_channel("commandes-bots", category=extra_cat)
            await update("✅ Salon bots créé")

        if session.deals_channel and extra_cat:
            deals_ch = await guild.create_text_channel("bons-plans", category=extra_cat)
            overwrites_deals = {guild.default_role: discord.PermissionOverwrite(send_messages=False)}
            await deals_ch.edit(overwrites=overwrites_deals)
            global DEALS_CHANNEL_ID
            DEALS_CHANNEL_ID = deals_ch.id
            await update("✅ Salon bons plans créé et verrouillé")

        if session.rules and rules_channel:
            rules_embed = discord.Embed(title="📋 Règlement du serveur", color=0xE74C3C)
            rules_embed.description = "\n".join([f"**{i+1}.** {r}" for i, r in enumerate(session.rules)])
            rules_embed.set_footer(text="En rejoignant ce serveur, vous acceptez ces règles.")
            await rules_channel.send(embed=rules_embed)
            await update("✅ Règlement publié")

        if session.welcome_message and welcome_channel:
            preview = discord.Embed(
                title="👋 Message de bienvenue",
                description=session.welcome_message.replace("{server}", guild.name).replace("{user}", session.user.display_name),
                color=VEGA_COLOR
            )
            await welcome_channel.send(embed=preview)
            await update("✅ Message de bienvenue configuré")

        del sessions[guild.id]

        final = discord.Embed(
            title="⚡ VEGA — Mission accomplie.",
            description=(
                f"Votre serveur **{session.server_name}** est opérationnel.\n\n"
                f"✅ **{len(created_roles)}** rôles créés\n"
                f"✅ **{len(tmpl.get('categories', []))}** catégories configurées\n"
                f"✅ Règlement & bienvenue en place\n\n"
                "*Tous les systèmes sont en ligne. Bonne continuation.*"
            ),
            color=0x2ECC71
        )
        final.set_footer(text="VEGA v1.0 • Setup terminé")
        await interaction.edit_original_response(embed=final)

    except discord.Forbidden:
        await interaction.edit_original_response(
            embed=vega_embed("Permissions insuffisantes", "❌ JARVIS n'a pas les droits nécessaires. Attribuez-lui le rôle **Administrateur**.", color=0xE74C3C)
        )
        if guild.id in sessions:
            del sessions[guild.id]
    except Exception as e:
        await interaction.edit_original_response(
            embed=vega_embed("Erreur système", f"❌ Une anomalie est survenue : `{e}`", color=0xE74C3C)
        )
        if guild.id in sessions:
            del sessions[guild.id]


# ═══════════════════════════════════════════
#  MUSIQUE
# ═══════════════════════════════════════════

music_queues = {}  # guild_id -> list of (url, title)
music_current = {}  # guild_id -> title

def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    return music_queues[guild_id]

@bot.tree.command(name="play", description="Joue une musique depuis un lien YouTube")
@app_commands.describe(lien="Lien YouTube ou recherche")
async def play(interaction: discord.Interaction, lien: str):
    if not interaction.user.voice:
        await interaction.response.send_message(
            embed=vega_embed("Musique — Erreur", "❌ Tu dois être dans un salon vocal !", color=0xE74C3C),
            ephemeral=True
        )
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel
    guild_id = interaction.guild.id

    try:
        import yt_dlp
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not lien.startswith("http"):
                lien = f"ytsearch1:{lien}"
            info = ydl.extract_info(lien, download=False)
            if "entries" in info:
                info = info["entries"][0]
            audio_url = info["url"]
            title = info.get("title", "Titre inconnu")
            duration = info.get("duration", 0)
            thumbnail = info.get("thumbnail", "")
            webpage_url = info.get("webpage_url", lien)

        # Connecter au vocal
        if interaction.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = interaction.guild.voice_client
            if vc.channel != channel:
                await vc.move_to(channel)

        # Ajouter à la queue ou jouer directement
        queue = get_queue(guild_id)

        if vc.is_playing():
            queue.append((audio_url, title, webpage_url))
            embed = vega_embed(
                "Musique — Ajouté à la file",
                f"**[{title}]({webpage_url})**\nPosition dans la file : #{len(queue)}"
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            await interaction.followup.send(embed=embed)
        else:
            music_current[guild_id] = title

            FFMPEG_OPTIONS = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -b:a 192k"
            }

            def after_playing(error):
                queue = get_queue(guild_id)
                if queue:
                    next_url, next_title, next_page = queue.pop(0)
                    music_current[guild_id] = next_title
                    source = discord.FFmpegPCMAudio(next_url, **FFMPEG_OPTIONS)
                    source = discord.PCMVolumeTransformer(source, volume=0.8)
                    vc.play(source, after=after_playing)

            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=0.8)
            vc.play(source, after=after_playing)

            mins, secs = divmod(duration, 60)
            embed = vega_embed(
                "🎵 Lecture en cours",
                f"**[{title}]({webpage_url})**\n⏱️ Durée : {mins}:{secs:02d}"
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            embed=vega_embed("Musique — Erreur", f"❌ Erreur : `{e}`\nAssure-toi que FFmpeg est installé.", color=0xE74C3C)
        )

@bot.tree.command(name="stop", description="Arrête la musique et déconnecte JARVIS du vocal")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        music_queues[interaction.guild.id] = []
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(embed=vega_embed("Musique", "⏹️ Musique arrêtée."))
    else:
        await interaction.response.send_message(embed=vega_embed("Musique", "Je ne suis pas dans un salon vocal."), ephemeral=True)

@bot.tree.command(name="skip", description="Passe à la musique suivante")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message(embed=vega_embed("Musique", "⏭️ Musique suivante !"))
    else:
        await interaction.response.send_message(embed=vega_embed("Musique", "Aucune musique en cours."), ephemeral=True)

@bot.tree.command(name="pause", description="Met en pause ou reprend la musique")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message(embed=vega_embed("Musique", "⏸️ Musique mise en pause."))
    elif vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message(embed=vega_embed("Musique", "▶️ Reprise de la musique."))
    else:
        await interaction.response.send_message(embed=vega_embed("Musique", "Aucune musique en cours."), ephemeral=True)

@bot.tree.command(name="queue", description="Affiche la file d'attente musicale")
async def queue_cmd(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    queue = get_queue(guild_id)
    current = music_current.get(guild_id, "Aucune")
    embed = vega_embed("🎵 File d'attente")
    embed.add_field(name="▶️ En cours", value=current, inline=False)
    if queue:
        q_text = "\n".join([f"{i+1}. {t}" for i, (_, t, _) in enumerate(queue[:10])])
        embed.add_field(name="📋 Suivantes", value=q_text, inline=False)
    else:
        embed.add_field(name="📋 File vide", value="Aucune musique en attente.", inline=False)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  GTA 6 COUNTDOWN + ALERTES ROCKSTAR
# ═══════════════════════════════════════════

GTA6_DATE = datetime(2026, 11, 19, 0, 0, 0)
GTA6_CHANNEL_ID = None  # Sera configuré via /gta6-setup
ROCKSTAR_LAST_POST = {}  # Pour éviter les doublons

@bot.tree.command(name="gta6", description="Affiche le compte à rebours jusqu'à la sortie de GTA 6")
async def gta6(interaction: discord.Interaction):
    now = datetime.now()
    if now >= GTA6_DATE:
        embed = vega_embed("🎮 GTA 6", "GTA 6 est sorti ! 🎉")
        await interaction.response.send_message(embed=embed)
        return

    delta = GTA6_DATE - now
    jours = delta.days
    heures, remainder = divmod(delta.seconds, 3600)
    minutes, secondes = divmod(remainder, 60)

    embed = discord.Embed(
        title="🎮 GTA 6 — Compte à rebours",
        description=(
            f"**Grand Theft Auto VI**\n"
            f"📅 Sortie prévue : **19 novembre 2026**\n\n"
            f"⏳ Il reste :\n"
            f"```\n{jours} jours\n{heures} heures\n{minutes} minutes\n{secondes} secondes\n```"
        ),
        color=0xFF6B00
    )
    embed.set_footer(text="VEGA • Données Rockstar Games")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gta6-setup", description="Configure le salon pour les alertes GTA 6 / Rockstar")
@app_commands.describe(salon="Le salon où envoyer les alertes")
@app_commands.checks.has_permissions(administrator=True)
async def gta6_setup(interaction: discord.Interaction, salon: discord.TextChannel):
    global GTA6_CHANNEL_ID
    GTA6_CHANNEL_ID = salon.id
    embed = vega_embed(
        "GTA 6 — Alertes configurées ✅",
        f"Les alertes Rockstar Games seront envoyées dans {salon.mention}.\n"
        f"VEGA surveille les publications de Rockstar Games en rapport avec GTA 6."
    )
    await interaction.response.send_message(embed=embed)
    if not check_rockstar.is_running():
        check_rockstar.start()

@tasks.loop(minutes=30)
async def check_rockstar():
    if not GTA6_CHANNEL_ID:
        return
    channel = bot.get_channel(GTA6_CHANNEL_ID)
    if not channel:
        return

    try:
        url = "https://www.rockstargames.com/newswire"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                text = await resp.text()

        # Cherche les titres d'articles contenant GTA 6
        import re as _re
        articles = _re.findall(r'<title[^>]*>([^<]+)</title>', text)
        for article in articles[:5]:
            art_lower = article.lower()
            if any(kw in art_lower for kw in ["gta 6", "gta vi", "grand theft auto 6", "grand theft auto vi"]):
                if article not in ROCKSTAR_LAST_POST:
                    ROCKSTAR_LAST_POST[article] = True
                    embed = discord.Embed(
                        title="🚨 Rockstar Games — Nouvelle publication GTA 6 !",
                        description=f"**{article}**\n[Voir sur Rockstar Newswire]({url})",
                        color=0xFF6B00
                    )
                    embed.set_footer(text="VEGA • Surveillance Rockstar Games")
                    await channel.send("@everyone", embed=embed)
    except:
        pass

# ═══════════════════════════════════════════
#  BONS PLANS JEUX VIDÉO
# ═══════════════════════════════════════════

DEALS_CHANNEL_ID = None
DEALS_LAST_SENT = []

@bot.tree.command(name="deals-setup", description="Configure le salon pour les bons plans jeux/PC")
@app_commands.describe(salon="Le salon réservé aux bons plans")
@app_commands.checks.has_permissions(administrator=True)
async def deals_setup(interaction: discord.Interaction, salon: discord.TextChannel):
    global DEALS_CHANNEL_ID
    DEALS_CHANNEL_ID = salon.id

    # Verrouiller le salon — seul le bot peut écrire
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    await salon.set_permissions(interaction.guild.default_role, overwrite=overwrite)

    embed = vega_embed(
        "Bons plans — Configuré ✅",
        f"Les bons plans seront postés dans {salon.mention}.\nLe salon est verrouillé — seul VEGA peut y écrire.\nVEGA postera les meilleures offres automatiquement."
    )
    await interaction.response.send_message(embed=embed)
    if not check_deals.is_running():
        check_deals.start()

@bot.tree.command(name="deals-now", description="Force la recherche de bons plans maintenant")
@app_commands.checks.has_permissions(administrator=True)
async def deals_now(interaction: discord.Interaction):
    await interaction.response.send_message(embed=vega_embed("Bons plans", "🔍 Recherche des meilleures offres en cours..."))
    await fetch_and_post_deals()

async def fetch_and_post_deals():
    if not DEALS_CHANNEL_ID:
        return
    channel = bot.get_channel(DEALS_CHANNEL_ID)
    if not channel:
        return

    try:
        # IsThereAnyDeal API (gratuite)
        url = "https://api.isthereanydeal.com/deals/v2?limit=5&sort=-cut&nondeals=0"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    deals = data.get("list", [])

                    if deals:
                        embed = discord.Embed(
                            title="🎮 Bons plans du moment",
                            description="Les meilleures réductions jeux vidéo sélectionnées par JARVIS",
                            color=0x00D4FF
                        )
                        for deal in deals[:5]:
                            title = deal.get("title", "Jeu inconnu")
                            cut = deal.get("cut", 0)
                            price = deal.get("price", {}).get("amount", "?")
                            shop = deal.get("shop", {}).get("name", "?")
                            url_deal = deal.get("url", "")
                            if title not in DEALS_LAST_SENT:
                                DEALS_LAST_SENT.append(title)
                                embed.add_field(
                                    name=f"🎮 {title}",
                                    value=f"-**{cut}%** → **{price}€** sur {shop}\n[Voir l'offre]({url_deal})",
                                    inline=False
                                )
                        if len(embed.fields) > 0:
                            await channel.send(embed=embed)
                            if len(DEALS_LAST_SENT) > 50:
                                DEALS_LAST_SENT.clear()
    except:
        # Fallback : deals manuels connus
        embed = discord.Embed(
            title="🎮 Bons plans jeux vidéo",
            description="Sites recommandés pour trouver les meilleures offres :",
            color=0x00D4FF
        )
        embed.add_field(name="🏪 Boutiques", value=(
            "[IsThereAnyDeal](https://isthereanydeal.com) — Comparateur de prix\n"
            "[Dealabs](https://www.dealabs.com/groupe/jeux-video) — Bons plans communauté\n"
            "[CDKeys](https://www.cdkeys.com) — Clés pas chères\n"
            "[Instant Gaming](https://www.instant-gaming.com) — Réductions permanentes"
        ), inline=False)
        await channel.send(embed=embed)

@tasks.loop(hours=6)
async def check_deals():
    await fetch_and_post_deals()



# ═══════════════════════════════════════════
#  DÉTECTION DU CONTEXTE DU SERVEUR
# ═══════════════════════════════════════════

SERVER_CONTEXTS = {}  # guild_id -> context info

SERVER_TYPES = {
    # Gaming & Esport
    "gaming": {
        "label": "🎮 Gaming",
        "keywords": ["gaming", "game", "jeu", "jeux", "play", "gamer", "xbox", "playstation", "nintendo", "pc", "valorant", "minecraft", "fortnite", "lol", "league", "csgo", "fps", "rpg", "mmorpg"],
        "color": 0x2ECC71,
        "suggestions": ["Tournois", "Stats de jeu", "Bons plans jeux", "Recherche équipe", "Tier list"],
        "personality": "Tu es passionné de gaming, tu parles le langage des gamers, tu connais les jeux populaires et tu aides la communauté à s'organiser."
    },
    "esport": {
        "label": "🏆 Esport",
        "keywords": ["esport", "esports", "compétitif", "competitive", "team", "équipe", "tournoi", "tournament", "pro", "ranked", "elo", "coaching", "scrim"],
        "color": 0xE74C3C,
        "suggestions": ["Organisation de tournois", "Recrutement", "Analyse de performances", "Planning d'entraînement"],
        "personality": "Tu es expert en esport, tu parles de stratégies, de méta, de performances et tu aides les équipes à s'organiser."
    },
    "gamedev": {
        "label": "🕹️ Game Dev",
        "keywords": ["gamedev", "game dev", "unity", "unreal", "godot", "développement jeu", "indie", "pixel art", "shader", "blender"],
        "color": 0x9B59B6,
        "suggestions": ["Aide au développement", "Ressources", "Feedback sur projets", "Game jam"],
        "personality": "Tu es expert en développement de jeux vidéo, tu connais les moteurs de jeu et tu aides les développeurs."
    },
    # Éducation
    "etudiant": {
        "label": "📚 Étudiant",
        "keywords": ["étude", "etude", "révision", "revision", "cours", "examen", "bac", "brevet", "licence", "master", "université", "lycée", "collège", "devoir", "homework", "school", "student"],
        "color": 0x3498DB,
        "suggestions": ["Fiches de révision", "Quiz", "Plan de révision", "Correction de devoirs", "Explication de cours"],
        "personality": "Tu es un assistant pédagogique bienveillant. Tu aides les étudiants à comprendre, mémoriser et progresser."
    },
    "coding": {
        "label": "💻 Coding / Dev",
        "keywords": ["code", "coding", "dev", "developer", "python", "javascript", "java", "html", "css", "github", "programmation", "programming", "bug", "api", "backend", "frontend"],
        "color": 0x1ABC9C,
        "suggestions": ["Aide au code", "Review de code", "Ressources dev", "Debug", "Projets collaboratifs"],
        "personality": "Tu es un développeur expert. Tu aides à débugger, expliques les concepts de programmation et proposes des solutions élégantes."
    },
    "langues": {
        "label": "🌍 Langues",
        "keywords": ["langue", "language", "anglais", "english", "espagnol", "spanish", "japonais", "japanese", "traduction", "translation", "grammaire", "vocabulary", "vocabulaire"],
        "color": 0xF39C12,
        "suggestions": ["Traduction", "Correction grammaticale", "Vocabulaire", "Exercices de langue", "Conversation"],
        "personality": "Tu es un professeur de langues polyglotte. Tu corriges, expliques et aides à progresser dans l'apprentissage des langues."
    },
    "professionnel": {
        "label": "💼 Professionnel",
        "keywords": ["pro", "professionnel", "entreprise", "business", "startup", "marketing", "rh", "management", "réunion", "meeting", "projet", "agile", "scrum"],
        "color": 0x2C3E50,
        "suggestions": ["Aide à la rédaction", "Organisation de réunions", "Résumés", "Brainstorming", "Gestion de projet"],
        "personality": "Tu es un assistant professionnel efficace. Tu aides à la productivité, la communication et l'organisation."
    },
    # Créatif
    "art": {
        "label": "🎨 Art / Design",
        "keywords": ["art", "dessin", "drawing", "illustration", "design", "graphisme", "photoshop", "illustrator", "figma", "créatif", "creative", "artwork", "fanart"],
        "color": 0xE91E63,
        "suggestions": ["Feedback sur créations", "Ressources artistiques", "Tutoriels", "Challenges créatifs", "Inspiration"],
        "personality": "Tu es un passionné d'art et de design. Tu donnes des feedbacks constructifs et encourages la créativité."
    },
    "musique": {
        "label": "🎵 Musique",
        "keywords": ["musique", "music", "beatmaking", "production", "dj", "rap", "rock", "jazz", "piano", "guitare", "guitar", "fl studio", "ableton", "mix", "sample"],
        "color": 0x8E44AD,
        "suggestions": ["Partage de musique", "Feedback", "Théorie musicale", "Ressources", "Collaborations"],
        "personality": "Tu es passionné de musique. Tu connais tous les genres, les techniques de production et tu aides les musiciens à progresser."
    },
    "ecriture": {
        "label": "✍️ Écriture",
        "keywords": ["écriture", "writing", "roman", "livre", "book", "poésie", "poetry", "fanfiction", "auteur", "author", "rédaction", "scénario", "script"],
        "color": 0xD35400,
        "suggestions": ["Feedback sur textes", "Correction", "Inspiration", "Développement de personnages", "World building"],
        "personality": "Tu es un écrivain passionné. Tu aides à développer des histoires, corriges les textes et inspires la créativité littéraire."
    },
    # Streaming & Contenu
    "streaming": {
        "label": "🎥 Streaming",
        "keywords": ["stream", "streaming", "twitch", "youtube", "content", "créateur", "creator", "live", "vod", "clip", "subscriber", "abonné"],
        "color": 0x9B59B6,
        "suggestions": ["Planning de streams", "Annonces", "Clips", "Interaction communauté", "Stats"],
        "personality": "Tu es expert en streaming et création de contenu. Tu aides le créateur à gérer sa communauté et à grandir."
    },
    "anime": {
        "label": "🌸 Anime / Manga",
        "keywords": ["anime", "manga", "otaku", "weeb", "naruto", "one piece", "dragon ball", "attack on titan", "demon slayer", "jujutsu", "cosplay", "japan", "japonais"],
        "color": 0xFF6B9D,
        "suggestions": ["Recommandations anime", "Discussions", "Quiz anime", "Actualités", "Fanart"],
        "personality": "Tu es un otaku passionné. Tu connais des centaines d'animes et mangas et tu aides la communauté à découvrir de nouvelles œuvres."
    },
    "cinema": {
        "label": "🎬 Cinéma / Séries",
        "keywords": ["film", "movie", "série", "series", "netflix", "cinema", "acteur", "réalisateur", "marvel", "dc", "disney", "horreur", "action", "thriller"],
        "color": 0xC0392B,
        "suggestions": ["Recommandations", "Critiques", "Quiz cinéma", "Soirées film", "Actualités"],
        "personality": "Tu es un cinéphile passionné. Tu connais le cinéma mondial et tu aides la communauté à découvrir des films et séries."
    },
    # Lifestyle
    "sport": {
        "label": "🏋️ Sport / Fitness",
        "keywords": ["sport", "fitness", "musculation", "gym", "football", "basketball", "running", "yoga", "nutrition", "workout", "entraînement", "coach"],
        "color": 0x27AE60,
        "suggestions": ["Programmes d'entraînement", "Nutrition", "Motivation", "Challenges", "Suivi de progression"],
        "personality": "Tu es un coach sportif motivant. Tu donnes des conseils d'entraînement, de nutrition et tu motives la communauté."
    },
    "cuisine": {
        "label": "🍳 Cuisine",
        "keywords": ["cuisine", "food", "recette", "recipe", "cooking", "chef", "restaurant", "gastronomie", "pâtisserie", "boulangerie", "vegan", "végétarien"],
        "color": 0xE67E22,
        "suggestions": ["Recettes", "Conseils culinaires", "Idées de repas", "Techniques de cuisine", "Partage de photos"],
        "personality": "Tu es un chef passionné. Tu partages des recettes, des techniques culinaires et inspires la communauté en cuisine."
    },
    "voyage": {
        "label": "✈️ Voyage",
        "keywords": ["voyage", "travel", "backpacker", "tourisme", "destination", "hotel", "visa", "passeport", "aventure", "roadtrip", "vanlife"],
        "color": 0x16A085,
        "suggestions": ["Destinations", "Conseils de voyage", "Itinéraires", "Bons plans", "Partage d'expériences"],
        "personality": "Tu es un voyageur passionné. Tu connais les meilleures destinations et tu aides la communauté à planifier leurs aventures."
    },
    # Finance
    "crypto": {
        "label": "💰 Crypto / Finance",
        "keywords": ["crypto", "bitcoin", "ethereum", "nft", "defi", "trading", "invest", "finance", "bourse", "action", "wallet", "blockchain", "web3"],
        "color": 0xF1C40F,
        "suggestions": ["Actualités crypto", "Analyse de marché", "Éducation financière", "Alertes prix", "Discussions"],
        "personality": "Tu es expert en crypto et finance. Tu expliques les concepts, analyses les marchés et aides la communauté à comprendre l'écosystème."
    },
    "entrepreneuriat": {
        "label": "🚀 Entrepreneuriat",
        "keywords": ["startup", "entrepreneur", "business", "projet", "idée", "investisseur", "pitch", "lean", "mvp", "croissance", "growth", "saas"],
        "color": 0x2980B9,
        "suggestions": ["Feedback sur projets", "Conseils business", "Networking", "Ressources", "Pitches"],
        "personality": "Tu es un mentor entrepreneurial. Tu aides les entrepreneurs à développer leurs projets et à surmonter les obstacles."
    },
    # Général
    "communaute": {
        "label": "👥 Communauté",
        "keywords": ["communauté", "community", "général", "general", "social", "amis", "friends", "discussion", "chat"],
        "color": 0x00D4FF,
        "suggestions": ["Discussions générales", "Événements", "Sondages", "Présentations", "Bonne humeur"],
        "personality": "Tu es un assistant communautaire chaleureux. Tu animes les discussions, organises des événements et crées de la cohésion."
    }
}

def detect_server_type(guild) -> dict:
    """Analyse le serveur et détecte son type."""
    # Collecter tous les textes du serveur
    texts = []
    texts.append(guild.name.lower())
    
    for channel in guild.channels:
        texts.append(channel.name.lower())
    
    for role in guild.roles:
        texts.append(role.name.lower())
    
    all_text = " ".join(texts)
    
    # Scorer chaque type
    scores = {}
    for server_type, data in SERVER_TYPES.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in all_text:
                score += 1
        if score > 0:
            scores[server_type] = score
    
    if not scores:
        return SERVER_TYPES["communaute"]
    
    best_type = max(scores, key=scores.get)
    return {**SERVER_TYPES[best_type], "type": best_type, "score": scores[best_type]}

def get_server_context(guild) -> dict:
    """Récupère ou détecte le contexte du serveur."""
    guild_id = guild.id
    if guild_id not in SERVER_CONTEXTS:
        SERVER_CONTEXTS[guild_id] = detect_server_type(guild)
    return SERVER_CONTEXTS[guild_id]

@bot.tree.command(name="context", description="Affiche le type de serveur détecté par VEGA")
async def context(interaction: discord.Interaction):
    ctx = get_server_context(interaction.guild)
    embed = discord.Embed(
        title=f"🔍 Contexte détecté — {ctx['label']}",
        color=ctx.get("color", VEGA_COLOR)
    )
    embed.add_field(
        name="💡 Suggestions adaptées",
        value="\n".join([f"• {s}" for s in ctx.get("suggestions", [])]),
        inline=False
    )
    embed.add_field(
        name="🎯 Comment changer",
        value="Utilise `/set-context` pour définir manuellement le type de ton serveur.",
        inline=False
    )
    embed.set_footer(text=f"VEGA v1.0 • Détection automatique")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="set-context", description="Définit manuellement le type de serveur")
@app_commands.describe(type_serveur="Le type de ton serveur")
@app_commands.choices(type_serveur=[
    app_commands.Choice(name="🎮 Gaming", value="gaming"),
    app_commands.Choice(name="🏆 Esport", value="esport"),
    app_commands.Choice(name="🕹️ Game Dev", value="gamedev"),
    app_commands.Choice(name="📚 Étudiant", value="etudiant"),
    app_commands.Choice(name="💻 Coding / Dev", value="coding"),
    app_commands.Choice(name="🌍 Langues", value="langues"),
    app_commands.Choice(name="💼 Professionnel", value="professionnel"),
    app_commands.Choice(name="🎨 Art / Design", value="art"),
    app_commands.Choice(name="🎵 Musique", value="musique"),
    app_commands.Choice(name="✍️ Écriture", value="ecriture"),
    app_commands.Choice(name="🎥 Streaming", value="streaming"),
    app_commands.Choice(name="🌸 Anime / Manga", value="anime"),
    app_commands.Choice(name="🎬 Cinéma / Séries", value="cinema"),
    app_commands.Choice(name="🏋️ Sport / Fitness", value="sport"),
    app_commands.Choice(name="🍳 Cuisine", value="cuisine"),
    app_commands.Choice(name="✈️ Voyage", value="voyage"),
    app_commands.Choice(name="💰 Crypto / Finance", value="crypto"),
    app_commands.Choice(name="🚀 Entrepreneuriat", value="entrepreneuriat"),
    app_commands.Choice(name="👥 Communauté générale", value="communaute"),
])
@app_commands.checks.has_permissions(administrator=True)
async def set_context(interaction: discord.Interaction, type_serveur: str):
    ctx = {**SERVER_TYPES[type_serveur], "type": type_serveur}
    SERVER_CONTEXTS[interaction.guild.id] = ctx
    
    embed = discord.Embed(
        title=f"✅ Contexte mis à jour — {ctx['label']}",
        description=f"VEGA va maintenant adapter son comportement à votre serveur **{ctx['label']}**.",
        color=ctx.get("color", VEGA_COLOR)
    )
    embed.add_field(
        name="💡 Fonctionnalités adaptées",
        value="\n".join([f"• {s}" for s in ctx.get("suggestions", [])]),
        inline=False
    )
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════
#  PACK ÉTUDIANT — VEGA PROFESSEUR
# ═══════════════════════════════════════════

# Stockage des sessions d'étude par utilisateur
study_sessions = {}  # user_id -> {cours, fiches, quiz, score}

async def call_vega_ai(prompt: str, max_tokens: int = 2000) -> str:
    """Appel direct à l'IA pour les fonctions étudiantes."""
    try:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Tu es un professeur expert et pédagogue. Tu réponds toujours en français. Tu es précis, clair et structuré."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                data = await resp.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "Erreur lors de la génération."
    except Exception as e:
        return f"Erreur : {e}"

@bot.tree.command(name="fiche", description="Génère une fiche de révision à partir d'un cours")
@app_commands.describe(cours="Colle ton cours ou le sujet à réviser")
async def fiche(interaction: discord.Interaction, cours: str):
    await interaction.response.defer()
    prompt = f"""Génère une fiche de révision complète et bien structurée pour ce cours :

{cours}

La fiche doit contenir :
1. 📌 Points clés (les notions essentielles à retenir)
2. 📖 Définitions importantes
3. 🔑 À retenir absolument (les 3-5 choses les plus importantes)
4. 💡 Astuces pour mémoriser

Sois concis mais complet. Utilise des emojis pour structurer."""

    fiche_text = await call_vega_ai(prompt, 1500)
    
    # Stocker pour les quiz
    user_id = interaction.user.id
    study_sessions[user_id] = {"cours": cours, "fiche": fiche_text, "quiz_score": 0}
    
    # Découper si trop long pour Discord
    if len(fiche_text) > 1900:
        parts = [fiche_text[i:i+1900] for i in range(0, len(fiche_text), 1900)]
        await interaction.followup.send(f"📚 **Fiche de révision** — {interaction.user.display_name}")
        for part in parts:
            await interaction.channel.send(part)
        await interaction.channel.send("✅ Tape `/quiz` pour tester tes connaissances sur ce cours !")
    else:
        await interaction.followup.send(f"📚 **Fiche de révision** — {interaction.user.display_name}\n\n{fiche_text}\n\n✅ Tape `/quiz` pour tester tes connaissances !")

@bot.tree.command(name="resume", description="Résume un texte long en points essentiels")
@app_commands.describe(texte="Le texte à résumer")
async def resume(interaction: discord.Interaction, texte: str):
    await interaction.response.defer()
    prompt = f"""Résume ce texte en points essentiels clairs et concis, en français :

{texte}

Format :
- Points essentiels numérotés
- Maximum 8 points
- Chaque point en 1-2 phrases maximum
- Commence par les infos les plus importantes"""

    result = await call_vega_ai(prompt, 800)
    await interaction.followup.send(f"📝 **Résumé** — {interaction.user.display_name}\n\n{result}")

@bot.tree.command(name="quiz", description="Lance un quiz sur ton dernier cours envoyé via /fiche")
async def quiz(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = interaction.user.id
    
    if user_id not in study_sessions or "cours" not in study_sessions[user_id]:
        await interaction.followup.send("❌ Tu n'as pas encore de cours chargé ! Utilise `/fiche` d'abord.")
        return
    
    cours = study_sessions[user_id]["cours"]
    prompt = f"""Génère 5 questions de QCM (choix multiples) sur ce cours :

{cours[:2000]}

Format STRICT (respecte exactement ce format) :
Q1: [question]
A) [réponse]
B) [réponse]
C) [réponse]
D) [réponse]
BONNE_REPONSE: [A/B/C/D]

Q2: ...etc

Génère exactement 5 questions variées et pertinentes."""

    quiz_text = await call_vega_ai(prompt, 1500)
    
    # Parser les questions
    questions = []
    current_q = {}
    for line in quiz_text.split("\n"):
        line = line.strip()
        if line.startswith("Q") and ":" in line and len(line) < 200:
            if current_q.get("question"):
                questions.append(current_q)
            current_q = {"question": line.split(":", 1)[1].strip(), "options": [], "answer": ""}
        elif line.startswith(("A)", "B)", "C)", "D)")):
            current_q.setdefault("options", []).append(line)
        elif line.startswith("BONNE_REPONSE:"):
            current_q["answer"] = line.replace("BONNE_REPONSE:", "").strip()
    if current_q.get("question"):
        questions.append(current_q)
    
    if not questions:
        await interaction.followup.send(f"📝 **Quiz généré :**\n\n{quiz_text}")
        return
    
    # Stocker le quiz
    study_sessions[user_id]["quiz"] = questions
    study_sessions[user_id]["quiz_index"] = 0
    study_sessions[user_id]["quiz_score"] = 0
    
    # Afficher la première question
    q = questions[0]
    msg = f"🎯 **Quiz — Question 1/{len(questions)}**\n\n**{q['question']}**\n\n"
    msg += "\n".join(q.get("options", []))
    msg += "\n\nRéponds avec la lettre : **A**, **B**, **C** ou **D**"
    
    await interaction.followup.send(msg)

@bot.tree.command(name="plan-revision", description="Génère un plan de révision personnalisé")
@app_commands.describe(
    matiere="La matière à réviser",
    jours="Combien de jours tu as pour réviser",
    niveau="Ton niveau actuel (débutant/intermédiaire/avancé)"
)
async def plan_revision(interaction: discord.Interaction, matiere: str, jours: int, niveau: str = "intermédiaire"):
    await interaction.response.defer()
    prompt = f"""Génère un plan de révision détaillé et réaliste pour :
- Matière : {matiere}
- Temps disponible : {jours} jours
- Niveau actuel : {niveau}

Le plan doit inclure :
📅 Planning jour par jour
⏱️ Temps suggéré par session (méthode Pomodoro)
📚 Ce qu'il faut réviser chaque jour
🎯 Objectifs concrets pour chaque session
💡 Conseils de mémorisation adaptés à la matière
✅ Comment savoir si tu es prêt

Sois réaliste et motivant !"""

    result = await call_vega_ai(prompt, 1500)
    
    if len(result) > 1900:
        parts = [result[i:i+1900] for i in range(0, len(result), 1900)]
        await interaction.followup.send(f"📅 **Plan de révision — {matiere}** ({jours} jours)")
        for part in parts:
            await interaction.channel.send(part)
    else:
        await interaction.followup.send(f"📅 **Plan de révision — {matiere}** ({jours} jours)\n\n{result}")

@bot.tree.command(name="explique", description="VEGA explique un concept de façon simple")
@app_commands.describe(
    concept="Le concept à expliquer",
    niveau="Pour quel niveau (lycée/université/débutant/expert)"
)
async def explique(interaction: discord.Interaction, concept: str, niveau: str = "lycée"):
    await interaction.response.defer()
    prompt = f"""Explique "{concept}" de façon claire et simple pour un niveau {niveau}.

Utilise :
- Des analogies et exemples concrets du quotidien
- Une progression logique du simple au complexe
- Des emojis pour illustrer
- Maximum 300 mots
- Termine par "En résumé :" avec 1-2 phrases clés"""

    result = await call_vega_ai(prompt, 600)
    await interaction.followup.send(f"💡 **{concept}** — Niveau {niveau}\n\n{result}")

@bot.tree.command(name="corrige", description="VEGA corrige ton texte ou ta rédaction")
@app_commands.describe(texte="Ton texte à corriger")
async def corrige(interaction: discord.Interaction, texte: str):
    await interaction.response.defer()
    prompt = f"""Corrige ce texte et améliore-le :

{texte}

Donne :
1. ✅ Version corrigée
2. 📝 Liste des erreurs trouvées (orthographe, grammaire, style)
3. 💡 Suggestions d'amélioration

Sois bienveillant et pédagogue."""

    result = await call_vega_ai(prompt, 1000)
    
    if len(result) > 1900:
        parts = [result[i:i+1900] for i in range(0, len(result), 1900)]
        await interaction.followup.send(f"✏️ **Correction** — {interaction.user.display_name}")
        for part in parts:
            await interaction.channel.send(part)
    else:
        await interaction.followup.send(f"✏️ **Correction** — {interaction.user.display_name}\n\n{result}")

# Gérer les réponses au quiz via on_message
async def handle_quiz_answer(message, user_id):
    """Gère les réponses au quiz en cours."""
    session = study_sessions.get(user_id, {})
    quiz = session.get("quiz", [])
    idx = session.get("quiz_index", 0)
    
    if not quiz or idx >= len(quiz):
        return False
    
    answer = message.content.strip().upper()
    if answer not in ["A", "B", "C", "D"]:
        return False
    
    q = quiz[idx]
    correct = q.get("answer", "").upper().strip()
    
    if answer == correct:
        study_sessions[user_id]["quiz_score"] = session.get("quiz_score", 0) + 1
        response = f"✅ **Bonne réponse !**"
    else:
        response = f"❌ **Mauvaise réponse.** La bonne réponse était **{correct}**."
    
    study_sessions[user_id]["quiz_index"] = idx + 1
    next_idx = idx + 1
    
    if next_idx >= len(quiz):
        score = study_sessions[user_id]["quiz_score"]
        total = len(quiz)
        pct = (score / total) * 100
        emoji = "🏆" if pct >= 80 else "📈" if pct >= 60 else "📚"
        response += f"\n\n{emoji} **Quiz terminé !** Score : **{score}/{total}** ({pct:.0f}%)"
        if pct < 60:
            response += "\n💡 Tu devrais revoir ta fiche avec `/fiche` !"
        elif pct >= 80:
            response += "\n🎉 Excellent travail, tu maîtrises le sujet !"
        await message.channel.send(response)
        study_sessions[user_id]["quiz"] = []
    else:
        next_q = quiz[next_idx]
        msg = f"{response}\n\n🎯 **Question {next_idx + 1}/{len(quiz)}**\n\n**{next_q['question']}**\n\n"
        msg += "\n".join(next_q.get("options", []))
        msg += "\n\nRéponds avec : **A**, **B**, **C** ou **D**"
        await message.channel.send(msg)
    
    return True

# ═══════════════════════════════════════════
#  LANCEMENT
# ═══════════════════════════════════════════
bot.run(TOKEN)
