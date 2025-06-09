# main.py
import discord
from discord.ext import commands
import estado
import partidas
import noche
import dia
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!mafia ", intents=intents)

@bot.command()
async def crear(ctx, cantidad: int):
    await partidas.crear_partida(ctx, cantidad)

@bot.command()
async def unirme(ctx):
    await partidas.unirse(ctx)

@bot.command()
async def matar(ctx, miembro: discord.Member):
    if ctx.channel != estado.mafioso_channel or ctx.author != estado.mafioso or estado.fase != "noche":
        await ctx.send("⚠️ No puedes usar este comando ahora.")
        return

    if not await partidas.esta_vivo(ctx.author) or not await partidas.esta_vivo(miembro):
        await ctx.send(f"⚠️ {miembro.mention} ya está muerto o tú estás muerto.")
        return

    estado.jugador_muerto = miembro
    await ctx.send(f"🔪 Has elegido a **{miembro.mention}** como tu víctima.")

@bot.command()
async def salvar(ctx, miembro: discord.Member):
    if ctx.author != estado.doctor or estado.fase != "noche":
        await ctx.send("⚠️ Solo el doctor puede usar este comando durante la noche.")
        return

    if not await partidas.esta_vivo(miembro):
        await ctx.send(f"⚠️ {miembro.mention} ya está muerto.")
        return

    estado.jugador_salvado = miembro
    await ctx.send(f"🩺 Has elegido salvar a **{miembro.mention}** esta noche.")

@bot.command()
async def votar(ctx, miembro: discord.Member):
    if estado.fase != "día":
        await ctx.send("⚠️ Solo puedes votar durante el día.")
        return

    if not await partidas.esta_vivo(ctx.author) or not await partidas.esta_vivo(miembro):
        await ctx.send(f"⚠️ {miembro.mention} o tú ya están muertos.")
        return

    if ctx.author in estado.votos:
        await ctx.send("⚠️ Ya votaste.")
        return

    estado.votos[ctx.author] = miembro
    await ctx.send(f"🗳️ {ctx.author.mention} ha votado por {miembro.mention}.")

    if len(estado.votos) == len(estado.jugadores):
        await dia.contar_votos(ctx)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))