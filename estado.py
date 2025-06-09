import random

async def elegir_aleatorio(vivos, excluir=None):
    candidatos = [j for j in vivos if j != excluir]
    return random.choice(candidatos) if candidatos else None


class NPC:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mention = f"**{nombre}**"

# Variables globales del estado del juego
jugadores = []
roles = {}
votos = {}

mafioso = None
doctor = None
detective = None

mafioso_channel = None
doctor_channel = None
detective_channel = None

fase = "día"
jugador_muerto = None
jugador_salvado = None

numero_esperado = 0
