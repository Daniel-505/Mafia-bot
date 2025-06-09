# partidas.py
import random
import discord
import estado
import noche

async def crear_partida(ctx, cantidad):
    if cantidad < 4:
        await ctx.send("⚠️ Se necesitan al menos 4 jugadores para empezar la partida.")
        return

    estado.jugadores.clear()
    estado.roles.clear()
    estado.votos.clear()

    guild = ctx.guild
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}

    estado.mafioso_channel = await guild.create_text_channel("mafioso-secreto", overwrites=overwrites)
    estado.doctor_channel = await guild.create_text_channel("doctor-secreto", overwrites=overwrites)
    estado.detective_channel = await guild.create_text_channel("detective-secreto", overwrites=overwrites)

    await ctx.send(f"¡La partida ha sido creada con {cantidad} jugadores! Usa !mafia unirme para entrar.")

async def unirse(ctx):
    if ctx.author in estado.jugadores:
        await ctx.send("⚠️ Ya estás en la partida.")
        return

    estado.jugadores.append(ctx.author)

    jugadores_lista = "\n".join([f"- {jugador.mention}" for jugador in estado.jugadores])
    await ctx.send(f"✅ {ctx.author.mention} se ha unido a la partida.\n\n📜 **Lista de jugadores:**\n{jugadores_lista}")

    if len(estado.jugadores) >= 4:
        await iniciar_partida(ctx)

async def iniciar_partida(ctx):
    random.shuffle(estado.jugadores)
    estado.mafioso, estado.doctor, estado.detective = estado.jugadores[:3]
    ciudadanos = estado.jugadores[3:]

    estado.roles[estado.mafioso] = "Mafioso"
    estado.roles[estado.doctor] = "Doctor"
    estado.roles[estado.detective] = "Detective"
    for ciudadano in ciudadanos:
        estado.roles[ciudadano] = "Ciudadano"

    await estado.mafioso_channel.set_permissions(estado.mafioso, read_messages=True, send_messages=True)
    await estado.doctor_channel.set_permissions(estado.doctor, read_messages=True, send_messages=True)
    await estado.detective_channel.set_permissions(estado.detective, read_messages=True, send_messages=True)

    for jugador, rol in estado.roles.items():
        try:
            mensaje = f"🎭 Tu rol en la partida es: **{rol}**.\n"
            if rol == "Mafioso":
                mensaje += f"😈 Puedes matar con !mafia matar @jugador cada noche en: {estado.mafioso_channel.jump_url}"
            elif rol == "Doctor":
                mensaje += f"🩺 Puedes salvar con !mafia salvar @jugador cada noche en: {estado.doctor_channel.jump_url}"
            elif rol == "Detective":
                mensaje += f"🔍 Puedes investigar a un jugador en: {estado.detective_channel.jump_url}"
            await jugador.send(mensaje)
        except:
            await ctx.send(f"⚠️ No pude enviar un mensaje privado a {jugador.mention}. Activa tus DMs.")

    estado.fase = "noche"
    await ctx.send("🏁 ¡La partida ha comenzado! La primera noche inicia ahora.")
    await noche.noche(ctx)

async def esta_vivo(jugador):
    return jugador in estado.jugadores

async def terminar_partida(ctx):
    await ctx.send("🏁 La partida ha terminado. Usa !mafia crear X para empezar otra.")

    for channel in [estado.mafioso_channel, estado.doctor_channel, estado.detective_channel]:
        if channel:
            await channel.delete()

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
