# logica_juego.py
from estado import jugadores, mafioso
from partidas import terminar_partida

async def verificar_ganador(ctx):
    from estado import fase

    if mafioso not in jugadores:
        await ctx.send("🎉 ¡El mafioso ha sido eliminado! **Los ciudadanos ganan.**")
        await terminar_partida(ctx)
        return

    if len(jugadores) == 1 and mafioso in jugadores:
        await ctx.send("🔪 El mafioso ha eliminado a todos. **Gana el mafioso.** 😈")
        await terminar_partida(ctx)
        return

    fase = "día"
