# bot-mafia

Guía de instalación y ejecución del bot de Mafia (Discord)

📁 PASOS PARA INSTALAR Y EJECUTAR

1. Clonar el repositorio:
   git clone https://github.com/usuario/bot-mafia.git
   cd bot-mafia
2. Instalar dependencias:
   pip install [discord.py](http://discord.py/)
3. Crear un bot en Discord:
   - Ir a https://discord.com/developers/applications
   - Crear nueva aplicación > ir a la pestaña "Bot"
   - Hacer clic en "Add Bot"
   - Copiar el token y pegarlo en el archivo .env, en TOKEN pegar tu token
   - Ir a "Privileged Gateway Intents" y activar "Message Content Intent"
4. Invitar el bot a tu servidor de Discord:
   - Ir a la pestaña "OAuth2" > "URL Generator"
   - Elegir "bot", y luego seleccionar permisos: "Administrator"
   - Copiar el enlace, abrirlo en el navegador, y agregar el bot a tu servidor
5. Ejecutar el bot:
   python main.py

📌 COMANDOS DISPONIBLES

- !mafia crear <número_de_jugadores>
- !mafia unirme <número_de_jugador>
- !mafia iniciar
- !mafia matar @jugador
- !mafia salvar @jugador
- !mafia votar @jugador

💡 IMPORTANTE:

- El token del bot va en la línea: DISCORD_BOT_TOKEN=TOKEN
- No compartir este token públicamente
- Esta versión del juego incluye fases de día y noche, comandos personalizados y condiciones de victoria
