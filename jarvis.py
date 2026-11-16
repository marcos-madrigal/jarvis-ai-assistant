import ollama
import os
from dotenv import load_dotenv
load_dotenv()

# Importamos nuestros propios módulos locales
from memoria import GestorMemoria
from gmail import GestorGmail
from calendario import GestorCalendario
from ejecutor import EjecutorAcciones
from voz import GestorVoz

class JarvisCore:
    def __init__(self):
        self.historial = [
            {
                "role": "system", 
                "content": "Eres J.A.R.V.I.S., un asistente de inteligencia artificial. Respondes de manera concisa, técnica y eficiente."
            }
        ]
        
        # --- PON AQUÍ TUS CREDENCIALES DE APPLE ---
        CORREO_ICLOUD = os.getenv("CORREO_ICLOUD", "")  # El correo con el que entras a Apple
        PASSWORD_APP = os.getenv("PASSWORD_APP_ICLOUD", "")       # La contraseña de aplicación generada
        # ------------------------------------------

        # Inicializamos los subsistemas
        self.memoria = GestorMemoria()
        self.gmail = GestorGmail()
        self.calendario = GestorCalendario(CORREO_ICLOUD, PASSWORD_APP)
        self.ejecutor = EjecutorAcciones(self.gmail, self.calendario)
        self.voz = GestorVoz()

        # Cargar memoria a largo plazo
        registros = self.memoria.cargar_ultimos(10)
        for rol, mensaje in registros:
            self.historial.append({"role": rol, "content": mensaje})

    def procesar(self, texto):
        self.historial.append({"role": "user", "content": texto})
        self.memoria.guardar("user", texto)
        
        # 1. Intentamos ejecutar una acción (abrir apps, leer/enviar correos, ver agenda)
        accion = self.ejecutor.analizar_y_ejecutar(texto)
        if accion:
            self.historial.append({"role": "assistant", "content": accion})
            self.memoria.guardar("assistant", accion)
            return accion
            
        # 2. Si no es un comando de acción, Llama 3.1 responde de forma normal
        try:
            respuesta = ollama.chat(model='llama3.1', messages=self.historial)
            texto_respuesta = respuesta['message']['content']
            
            self.historial.append({"role": "assistant", "content": texto_respuesta})
            self.memoria.guardar("assistant", texto_respuesta)
            return texto_respuesta
            
        except Exception as e:
            return f"Error en los sistemas locales: {str(e)}"


if __name__ == "__main__":
    print("Iniciando sistemas locales... J.A.R.V.I.S. en línea.")
    
    # 1. Preguntamos el modo de operación al arrancar
    modo = input("¿Desea iniciar en Modo Voz (v) o Modo Silencioso (s)? [v/s]: ").lower()
    modo_voz = modo == 'v'

    asistente = JarvisCore()
    
    # 2. Saludo dependiendo del modo
    if modo_voz:
        asistente.voz.hablar("Sistemas inicializados. Estoy a su disposición, señor.")
    else:
        print("\nJ.A.R.V.I.S.: [Modo Silencioso Activado]")
        print("J.A.R.V.I.S.: Sistemas inicializados. Estoy a su disposición, señor.")
    
    while True:
        # 3. Escucha o lee dependiendo del modo
        if modo_voz:
            usuario = asistente.voz.escuchar()
            if not usuario:
                continue # Si hay silencio, vuelve a escuchar
        else:
            usuario = input("\nTú: ")
            if not usuario.strip():
                continue # Si pulsas Enter sin querer, vuelve a preguntar
            
        if usuario.lower() in ['salir', 'apagar', 'exit', 'adiós', 'adios', 'gracias adios']:
            if modo_voz:
                asistente.voz.hablar("Apagando sistemas. Que tenga un excelente día, señor.")
            else:
                print("J.A.R.V.I.S.: Apagando sistemas. Que tenga un excelente día, señor.")
            break
            
        print("J.A.R.V.I.S.: [Procesando solicitud en local...]") 
        respuesta = asistente.procesar(usuario)
        
        # 4. Responde hablando o escribiendo dependiendo del modo
        if modo_voz:
            asistente.voz.hablar(respuesta)
        else:
            # Quitamos los asteriscos de Llama 3.1 para que se lea mejor en terminal
            texto_limpio = respuesta.replace('*', '').replace('#', '')
            print(f"J.A.R.V.I.S.: {texto_limpio}")