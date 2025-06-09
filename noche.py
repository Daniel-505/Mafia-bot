import estado
import random
import asyncio
import discord

def nombre_mencion(jugador):
    return jugador.mention if isinstance(jugador, discord.Member) else jugador.nombre

async def noche(ctx):
    async def anunciar_inicio():
        await ctx.send("🌙 La noche ha comenzado. Mafioso, Doctor y Detective, realicen sus acciones.")

    async def acciones_npc():
        vivos = [j for j in estado.jugadores if j != estado.jugador_muerto]

        # Mafioso NPC elige a alguien al azar
        if isinstance(estado.mafioso, estado.NPC):
            objetivos = [j for j in vivos if j != estado.mafioso]
            if objetivos:
                estado.jugador_muerto = random.choice(objetivos)
                await ctx.send(f"🤖 El mafioso ha elegido a **{nombre_mencion(estado.jugador_muerto)}** como su víctima.")

        # Doctor NPC elige a alguien al azar
        if isinstance(estado.doctor, estado.NPC):
            estado.jugador_salvado = random.choice(vivos)
            await ctx.send(f"🤖 El doctor ha decidido salvar a **{nombre_mencion(estado.jugador_salvado)}** esta noche.")

        # Detective NPC elige a alguien al azar
        if isinstance(estado.detective, estado.NPC):
            objetivo = random.choice([j for j in vivos if j != estado.detective])
            rol = estado.roles.get(objetivo, "Desconocido")
            await ctx.send(f"🔍 El detective investigó a **{nombre_mencion(objetivo)}** y descubrió que es **{rol}**.")

    async def esperar_acciones():
        await asyncio.sleep(5)  # Simula tiempo de noche si es necesario

    async def procesar_resultado():
        if estado.jugador_muerto and estado.jugador_muerto != estado.jugador_salvado:
            await ctx.send(f"💀 **{nombre_mencion(estado.jugador_muerto)}** ha muerto esta noche.")
            estado.jugadores.remove(estado.jugador_muerto)
            estado.roles.pop(estado.jugador_muerto, None)
        else:
            await ctx.send("💤 Nadie murió esta noche.")

    async def terminar():
        estado.jugador_muerto = None
        estado.jugador_salvado = None
        estado.votos.clear()
        estado.fase = "día"
        await ctx.send("☀️ Ha amanecido. Usa `!mafia votar @jugador` para votar.")

    await anunciar_inicio()
    await acciones_npc()
    await esperar_acciones()
    await procesar_resultado()
    await terminar()
