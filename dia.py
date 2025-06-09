import estado
import discord
import random
import asyncio

async def npc_votar(ctx):
    # NPC que aún no votaron
    for jugador in estado.jugadores:
        if isinstance(jugador, estado.NPC) and jugador not in estado.votos:
            # Objetivos posibles (vivos, distintos del NPC)
            posibles_objetivos = [j for j in estado.jugadores if j != jugador and j in estado.jugadores]
            if posibles_objetivos:
                elegido = random.choice(posibles_objetivos)
                estado.votos[jugador] = elegido
                nombre_objetivo = elegido.mention if isinstance(elegido, discord.Member) else elegido.nombre
                await ctx.send(f"🤖 {jugador.nombre} ha votado por {nombre_objetivo}.")

    # Si todos ya votaron, contar votos
    if len(estado.votos) == len(estado.jugadores):
        await contar_votos(ctx)


async def contar_votos(ctx):
    if not estado.votos:
        await ctx.send("⚠️ Nadie ha votado.")
        return

    # Contar votos
    conteo = {}
    for votante, votado in estado.votos.items():
        conteo[votado] = conteo.get(votado, 0) + 1

    # Mostrar resultados
    mensaje_resultados = "🗳️ **Resultado de la votación:**\n"
    for jugador, votos in conteo.items():
        nombre = jugador.mention if isinstance(jugador, discord.Member) else jugador.nombre
        mensaje_resultados += f"- {nombre}: {votos} voto(s)\n"

    await ctx.send(mensaje_resultados)

    # Determinar el más votado
    max_votos = max(conteo.values())
    candidatos = [j for j, v in conteo.items() if v == max_votos]

    if len(candidatos) > 1:
        await ctx.send("🤷 Hubo un empate. Nadie será eliminado hoy.")
    else:
        eliminado = candidatos[0]
        nombre = eliminado.mention if isinstance(eliminado, discord.Member) else eliminado.nombre
        await ctx.send(f"☠️ {nombre} ha sido eliminado por votación.")
        if eliminado in estado.jugadores:
            estado.jugadores.remove(eliminado)
        estado.roles.pop(eliminado, None)

    # Resetear estado
    estado.votos.clear()
    estado.fase = "noche"

    await ctx.send("🌙 Comienza la noche. Usa `!mafia noche` para continuar.")
