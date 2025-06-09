# noche.py
import asyncio
import estado
from dia import verificar_ganador

async def eliminar_permisos(jugador):
    if estado.mafioso_channel:
        await estado.mafioso_channel.set_permissions(jugador, read_messages=False, send_messages=False)
    if estado.doctor_channel:
        await estado.doctor_channel.set_permissions(jugador, read_messages=False, send_messages=False)
    if estado.detective_channel:
        await estado.detective_channel.set_permissions(jugador, read_messages=False, send_messages=False)

async def noche(ctx):
    estado.fase = "noche"
    estado.jugador_muerto = None
    estado.jugador_salvado = None

    await ctx.send("🌙 Es de noche. Todos los jugadores duermen...")
    await asyncio.sleep(60)  # Puedes ajustar el tiempo según tu preferencia
    await amanecer(ctx)

async def amanecer(ctx):
    estado.fase = "día"

    if estado.jugador_muerto is not None and estado.jugador_muerto == estado.jugador_salvado:
        await ctx.send(f"☀️ Amanece y **{estado.jugador_salvado.name}** fue atacado, ¡pero el doctor lo salvó! 🩺")
        estado.jugador_muerto = None
    elif estado.jugador_muerto is not None:
        await ctx.send(f"☀️ Amanece y encontramos el cuerpo de **{estado.jugador_muerto.name}**. Era **{estado.roles.get(estado.jugador_muerto, 'Desconocido')}**.")
        if estado.jugador_muerto in estado.jugadores:
            estado.jugadores.remove(estado.jugador_muerto)
        if estado.jugador_muerto in estado.roles:
            del estado.roles[estado.jugador_muerto]

    estado.jugador_salvado = None
    await verificar_ganador(ctx)

    if estado.fase == "día":
        await ctx.send("Es el momento de votar. Usen !mafia votar @jugador para elegir a alguien.")
