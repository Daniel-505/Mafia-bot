import random
import discord
import estado
import noche

async def crear_partida(ctx, cantidad):
    if cantidad < 4:
        await ctx.send("⚠️ Se necesitan al menos 4 jugadores.")
        return

    estado.jugadores.clear()
    estado.roles.clear()
    estado.votos.clear()
    estado.numero_esperado = cantidad  # Guardar cuántos jugadores se esperan

    guild = ctx.guild
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}

    estado.mafioso_channel = await guild.create_text_channel("mafioso-secreto", overwrites=overwrites)
    estado.doctor_channel = await guild.create_text_channel("doctor-secreto", overwrites=overwrites)
    estado.detective_channel = await guild.create_text_channel("detective-secreto", overwrites=overwrites)

    await ctx.send(f"🎲 Partida creada para {cantidad} jugadores.\nUsa `!mafia unirme`.\nCuando estés listo, usa `!mafia iniciar` y si faltan jugadores se autocompleta con Bots.")

async def unirse(ctx):
    if ctx.author in estado.jugadores:
        await ctx.send("⚠️ Ya estás en la partida.")
        return

    estado.jugadores.append(ctx.author)

    jugadores_lista = "\n".join([f"- {jugador.mention}" if isinstance(jugador, discord.Member) else f"- {jugador.nombre}" for jugador in estado.jugadores])
    await ctx.send(f"✅ {ctx.author.mention} se ha unido a la partida.\n📜 Lista:\n{jugadores_lista}")

async def agregar_npc(ctx):
    npc_num = sum(not isinstance(j, discord.Member) for j in estado.jugadores) + 1
    nuevo_npc = estado.NPC(f"NPC {npc_num}")
    estado.jugadores.append(nuevo_npc)
    await ctx.send(f"🤖 Se ha unido un bot: **{nuevo_npc.nombre}**")

import random

async def iniciar_partida(ctx):
    MIN_JUGADORES = 4

    # Completar automáticamente con NPCs si faltan
    while len(estado.jugadores) < estado.numero_esperado:
        npc_id = sum(isinstance(j, estado.NPC) for j in estado.jugadores) + 1
        nuevo_npc = estado.NPC(f"NPC {npc_id}")
        estado.jugadores.append(nuevo_npc)
        await ctx.send(f"🤖 Se ha agregado automáticamente: {nuevo_npc.mention}")

    if len(estado.jugadores) < MIN_JUGADORES:
        await ctx.send("⚠️ Se necesitan al menos 4 jugadores para iniciar.")
        return

    jugadores = estado.jugadores.copy()
    random.shuffle(jugadores)

    estado.mafioso = jugadores[0]
    estado.doctor = jugadores[1]
    estado.detective = jugadores[2]
    ciudadanos = jugadores[3:]

    estado.roles[estado.mafioso] = "Mafioso"
    estado.roles[estado.doctor] = "Doctor"
    estado.roles[estado.detective] = "Detective"
    for c in ciudadanos:
        estado.roles[c] = "Ciudadano"

    if isinstance(estado.mafioso, discord.Member):
        await estado.mafioso_channel.set_permissions(estado.mafioso, read_messages=True, send_messages=True)
    if isinstance(estado.doctor, discord.Member):
        await estado.doctor_channel.set_permissions(estado.doctor, read_messages=True, send_messages=True)
    if isinstance(estado.detective, discord.Member):
        await estado.detective_channel.set_permissions(estado.detective, read_messages=True, send_messages=True)

    npcs_mostrados = 0
    for jugador, rol in estado.roles.items():
        if isinstance(jugador, discord.Member):
            mensaje = f"🎭 Tu rol es: **{rol}**.\n"
            if rol == "Mafioso":
                mensaje += f"😈 Usa `!mafia matar @jugador` o `!mafia matar NPC <numero>` en: {estado.mafioso_channel.jump_url}"
            elif rol == "Doctor":
                mensaje += f"🩺 Usa `!mafia salvar @jugador` o `!mafia salvar NPC <numero>` en: {estado.doctor_channel.jump_url}"
            elif rol == "Detective":
                mensaje += f"🔍 Usa `!mafia investigar @jugador` o `!mafia investigar NPC <numero>` en: {estado.detective_channel.jump_url}"
            try:
                await jugador.send(mensaje)
            except:
                await ctx.send(f"⚠️ No pude enviar DM a {jugador.mention}.")
        else:
            # Solo muestra que el NPC se ha unido, sin mostrar su rol
            await ctx.send(f"{jugador.mention} se ha unido a la partida.")


    estado.fase = "noche"
    await ctx.send("🌙 ¡La partida ha comenzado! Usa `!mafia noche` para iniciar la primera noche.")

async def iniciar_noche(ctx):
    await noche.noche(ctx)

async def esta_vivo(jugador):
    return jugador in estado.jugadores

async def terminar_partida(ctx):
    await ctx.send("🏁 La partida ha terminado.")

    for canal in [estado.mafioso_channel, estado.doctor_channel, estado.detective_channel]:
        if canal:
            await canal.delete()

    estado.jugadores.clear()
    estado.roles.clear()
    estado.votos.clear()
    estado.mafioso_channel = None
    estado.doctor_channel = None
    estado.detective_channel = None
    estado.mafioso = None
    estado.doctor = None
    estado.detective = None
    estado.fase = "día"
    estado.jugador_muerto = None
    estado.jugador_salvado = None
    estado.jugadores_esperados = 0
