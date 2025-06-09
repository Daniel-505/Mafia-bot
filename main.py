import discord
from discord.ext import commands
import estado
import partidas
import noche
import dia
import random
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!mafia ", intents=intents)

# ────── 📦 Comandos de administración ──────

@bot.command()
async def crear(ctx, cantidad: int):
    await partidas.crear_partida(ctx, cantidad)

@bot.command()
async def unirme(ctx):
    await partidas.unirse(ctx)

@bot.command()
async def npc(ctx):
    await partidas.agregar_npc(ctx)

@bot.command()
async def iniciar(ctx):
    await partidas.iniciar_partida(ctx)

@bot.command()
async def terminar(ctx):
    await partidas.terminar_partida(ctx)

# ────── 🌙 Comandos de noche ──────

@bot.command()
async def noche(ctx):
    await partidas.iniciar_noche(ctx)


@bot.command()
async def matar(ctx, *, objetivo: str):
    if ctx.channel != estado.mafioso_channel or ctx.author != estado.mafioso or estado.fase != "noche":
        await ctx.send("⚠️ No puedes usar este comando ahora.")
        return

    objetivo = objetivo.strip().lower()

    # Buscar jugador humano por nombre o mención
    miembro = next(
        (j for j in estado.jugadores
         if isinstance(j, discord.Member)
         and (j.name.lower() == objetivo or j.display_name.lower() == objetivo or j.mention == objetivo)),
        None
    )

    # Si no es humano, buscar si es un NPC
    if not miembro:
        miembro = next((j for j in estado.jugadores
                        if isinstance(j, estado.NPC)
                        and j.nombre.lower() == objetivo), None)

    if not miembro:
        await ctx.send("⚠️ Jugador no encontrado.")
        return

    if not await partidas.esta_vivo(ctx.author) or not await partidas.esta_vivo(miembro):
        nombre = miembro.mention if isinstance(miembro, discord.Member) else miembro.nombre
        await ctx.send(f"⚠️ {nombre} ya está muerto o tú estás muerto.")
        return

    estado.jugador_muerto = miembro
    nombre = miembro.mention if isinstance(miembro, discord.Member) else miembro.nombre
    await ctx.send(f"🔪 Has elegido matar a **{nombre}**.")

@bot.command()
async def investigar(ctx, *, objetivo: str):
    if ctx.author != estado.detective or estado.fase != "noche":
        await ctx.send("⚠️ Solo el detective puede usar este comando durante la noche.")
        return

    # Buscar objetivo entre jugadores
    investigado = None
    for jugador in estado.jugadores:
        nombre = jugador.display_name if isinstance(jugador, discord.Member) else jugador.nombre
        if objetivo.lower() == nombre.lower():
            investigado = jugador
            break

    if not investigado:
        await ctx.send("⚠️ No encontré a ese jugador para investigar.")
        return

    if not await partidas.esta_vivo(investigado):
        await ctx.send("⚠️ Ese jugador ya está muerto.")
        return

    es_mafioso = estado.roles.get(investigado) == "Mafioso"
    resultado = f"{investigado.mention if isinstance(investigado, discord.Member) else investigado.nombre} **es** Mafioso." \
        if es_mafioso else f"{investigado.mention if isinstance(investigado, discord.Member) else investigado.nombre} **no es** Mafioso."

    try:
        await ctx.author.send(f"🔎 Resultado de tu investigación: {resultado}")
    except:
        await ctx.send("⚠️ No pude enviarte el resultado por mensaje privado.")


@bot.command()
async def salvar(ctx, *, objetivo: str):
    if ctx.author != estado.doctor or estado.fase != "noche":
        await ctx.send("⚠️ Solo el doctor puede usar este comando durante la noche.")
        return

    objetivo = objetivo.strip().lower()

    # Buscar humano
    miembro = next(
        (j for j in estado.jugadores if isinstance(j, discord.Member)
         and (j.name.lower() == objetivo or j.display_name.lower() == objetivo or j.mention == objetivo)),
        None
    )

    # Buscar NPC
    if not miembro:
        miembro = next((j for j in estado.jugadores
                        if isinstance(j, estado.NPC)
                        and j.nombre.lower() == objetivo), None)

    if not miembro:
        await ctx.send("⚠️ Jugador no encontrado.")
        return

    if not await partidas.esta_vivo(miembro):
        nombre = miembro.mention if isinstance(miembro, discord.Member) else miembro.nombre
        await ctx.send(f"⚠️ {nombre} ya está muerto.")
        return

    estado.jugador_salvado = miembro
    nombre = miembro.mention if isinstance(miembro, discord.Member) else miembro.nombre
    await ctx.send(f"🩺 Has elegido salvar a **{nombre}** esta noche.")


# ────── ☀️ Comandos de día ──────

@bot.command()
async def votar(ctx, *, nombre: str):
    if estado.fase != "día":
        await ctx.send("⚠️ Solo puedes votar durante el día.")
        return

    objetivo = None
    nombre = nombre.lower().strip()

    for jugador in estado.jugadores:
        if isinstance(jugador, discord.Member):
            if nombre in [jugador.mention.lower(), jugador.name.lower(), jugador.display_name.lower()]:
                objetivo = jugador
                break
        else:
            if nombre == jugador.nombre.lower():
                objetivo = jugador
                break

    if objetivo is None:
        await ctx.send(f"⚠️ No encontré al jugador `{nombre}` para votar.")
        return

    if ctx.author not in estado.jugadores:
        await ctx.send(f"⚠️ {ctx.author.mention}, no estás en la partida o ya estás muerto.")
        return

    if ctx.author in estado.votos:
        await ctx.send("⚠️ Ya votaste.")
        return

    estado.votos[ctx.author] = objetivo
    objetivo_nombre = objetivo.mention if isinstance(objetivo, discord.Member) else objetivo.nombre
    await ctx.send(f"🗳️ {ctx.author.mention} ha votado por {objetivo_nombre}.")

    # Ahora votan los NPC automáticamente
    await npc_votar(ctx)

    # Comprobar si todos votaron (humanos + NPCs)
    if len(estado.votos) >= len(estado.jugadores):
        import dia  # donde tengas la función contar_votos
        await dia.contar_votos(ctx)


async def npc_votar(ctx):
    npc_jugadores = [j for j in estado.jugadores if not isinstance(j, discord.Member)]

    for npc in npc_jugadores:
        # NPC elige aleatoriamente a alguien que no sea él mismo
        posibles_objetivos = [j for j in estado.jugadores if j != npc]
        if posibles_objetivos:
            elegido = random.choice(posibles_objetivos)
            estado.votos[npc] = elegido
            objetivo_nombre = elegido.mention if isinstance(elegido, discord.Member) else elegido.nombre
            await ctx.send(f"🤖 {npc.nombre} ha votado por {objetivo_nombre}.")


# ────── ✅ Iniciar el bot ──────

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
