# dia.py
import estado
import noche
import partidas

async def verificar_ganador(ctx):
    if estado.mafioso not in estado.jugadores:
        await ctx.send("🎉 ¡El mafioso ha sido eliminado! **Los ciudadanos ganan.**")
        await partidas.terminar_partida(ctx)
        return

    if len(estado.jugadores) == 1 and estado.mafioso in estado.jugadores:
        await ctx.send("🔪 El mafioso ha eliminado a todos. **Gana el mafioso.** 😈")
        await partidas.terminar_partida(ctx)
        return

    estado.fase = "día"

async def contar_votos(ctx):
    if not estado.votos:
        await ctx.send("⚠️ Nadie votó. La ronda continúa sin eliminaciones.")
        estado.votos.clear()
        await noche.noche(ctx)
        return

    conteo = {}
    for voto in estado.votos.values():
        conteo[voto] = conteo.get(voto, 0) + 1

    max_votos = max(conteo.values(), default=0)
    candidatos = [jugador for jugador, votos in conteo.items() if votos == max_votos]

    if len(candidatos) > 1:
        await ctx.send("⚠️ Hubo un empate en la votación. Nadie es eliminado esta ronda.")
        estado.votos.clear()
        await noche.noche(ctx)
        return

    jugador_eliminado = candidatos[0]
    await ctx.send(f"🔪 **{jugador_eliminado.name}** ha sido eliminado. Era **{estado.roles[jugador_eliminado]}**.")

    if jugador_eliminado in estado.jugadores:
        estado.jugadores.remove(jugador_eliminado)
    if jugador_eliminado in estado.roles:
        del estado.roles[jugador_eliminado]

    await noche.eliminar_permisos(jugador_eliminado)

    estado.votos.clear()

    if jugador_eliminado == estado.mafioso:
        await ctx.send("🎉 ¡El mafioso ha sido eliminado! **Los ciudadanos ganan.**")
        await partidas.terminar_partida(ctx)
        return

    await noche.noche(ctx)
