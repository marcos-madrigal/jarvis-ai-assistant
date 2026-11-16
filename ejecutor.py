import subprocess
import webbrowser
import json
from datetime import datetime, timedelta
import ollama
import re
import threading
import winsound

class EjecutorAcciones:
    def __init__(self, gestor_gmail, gestor_calendario):
        self.gmail = gestor_gmail
        self.calendario = gestor_calendario

    def analizar_y_ejecutar(self, texto):
        texto_limpio = texto.lower()
        
        # --- FILTRO ANTI-TILDES PARA EVITAR ALUCINACIONES ---
        texto_sin_acentos = texto_limpio.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        
        if "bloc de notas" in texto_sin_acentos:
            subprocess.Popen(['notepad.exe'])
            return "He abierto el bloc de notas por usted, señor."
            
        elif "calculadora" in texto_sin_acentos:
            subprocess.Popen(['calc.exe'])
            return "Calculadora en pantalla."

        # --- LÓGICA DEL RELOJ DE WINDOWS Y TEMPORIZADOR INTERNO ---
        elif "temporizador" in texto_sin_acentos:
            # Usamos nuestro propio motor en lugar del de Windows
            return self._procesar_temporizador(texto)
            
        elif any(palabra in texto_sin_acentos for palabra in ["reloj", "cronometro", "alarma"]):
            if "cronometro" in texto_sin_acentos:
                subprocess.Popen('start ms-clock:stopwatch', shell=True)
                return "He abierto el cronómetro del sistema, señor."
            elif "alarma" in texto_sin_acentos:
                subprocess.Popen('start ms-clock:alarm', shell=True)
                return "He abierto sus alarmas del sistema, señor."
            else:
                subprocess.Popen('start ms-clock:', shell=True)
                return "He abierto la aplicación del reloj."
            
        elif "busca en google" in texto_sin_acentos:
            busqueda = texto_limpio.split("busca en google")[-1].strip()
            webbrowser.open(f"https://www.google.com/search?q={busqueda}")
            return f"He abierto una pestaña buscando: '{busqueda}'."
            
        # --- LÓGICA DE CREACIÓN DE EVENTOS ---
        elif any(palabra in texto_sin_acentos for palabra in ["añade", "crea", "programa"]) and any(palabra in texto_sin_acentos for palabra in ["evento", "reunion", "clase", "practica", "tutoria", "agenda", "examen"]):
            return self._procesar_creacion_evento(texto)

        # --- LÓGICA DE ELIMINACIÓN DE EVENTOS ---
        elif any(palabra in texto_sin_acentos for palabra in ["elimina", "borra", "cancela", "quita"]) and any(palabra in texto_sin_acentos for palabra in ["evento", "reunion", "clase", "practica", "tutoria", "agenda", "examen"]):
            return self._procesar_eliminacion_evento(texto)
            
        # --- LÓGICA DE LECTURA DE CALENDARIO ---
        elif "calendario" in texto_sin_acentos or "agenda" in texto_sin_acentos or "eventos" in texto_sin_acentos:
            print("J.A.R.V.I.S.: [Consultando iCloud Calendar...]")
            
            dias = 7  # Por defecto mira una semana
            if "hoy" in texto_sin_acentos:
                dias = 1
            elif "mañana" in texto_sin_acentos or "manana" in texto_sin_acentos:
                dias = 2
            elif "mes" in texto_sin_acentos:
                dias = 30
                
            eventos = self.calendario.obtener_eventos(dias=dias)
            return f"He revisado su agenda de iCloud. {eventos}"

        # --- LÓGICA DE GMAIL ---
        elif "envía un correo a" in texto_limpio or "envia un correo a" in texto_limpio:
            try:
                if " diciendo " in texto_limpio:
                    separador_cuerpo = " diciendo "
                elif " que diga " in texto_limpio:
                    separador_cuerpo = " que diga "
                else:
                    return "Formato incorrecto. Use: 'envía un correo a [email] con asunto [asunto] diciendo [mensaje]'."
                
                partes = texto_limpio.split(" a ", 1)[1]
                resto, cuerpo = partes.split(separador_cuerpo, 1)
                
                if " con asunto " in resto:
                    destinatario, asunto = resto.split(" con asunto ", 1)
                else:
                    destinatario = resto
                    asunto = "Mensaje enviado por J.A.R.V.I.S."
                
                destinatario = destinatario.replace(" ", "").strip()
                asunto = asunto.strip().capitalize()
                cuerpo = cuerpo.strip().capitalize()
                
                print(f"J.A.R.V.I.S.: [Enviando correo a {destinatario} con asunto '{asunto}'...]")
                return self.gmail.enviar_correo(destinatario, asunto, cuerpo)
            except Exception:
                return "No he podido estructurar el envío."
            
        elif "resume" in texto_limpio and ("correo" in texto_limpio or "mensaje" in texto_limpio):
            indice = 0
            if any(p in texto_limpio for p in ["2", "segundo", "dos"]):
                indice = 1
            elif any(p in texto_limpio for p in ["3", "tercer", "tres"]):
                indice = 2
                
            if not self.gmail.ultimos_ids or len(self.gmail.ultimos_ids) <= indice:
                return "No tengo registro de ese correo. Pídame que revise la bandeja primero."
                
            print(f"J.A.R.V.I.S.: [Descargando e interpretando correo {indice + 1}...]")
            id_correo = self.gmail.ultimos_ids[indice]
            cuerpo = self.gmail.obtener_cuerpo_correo(id_correo)
            
            prompt_resumen = f"Eres J.A.R.V.I.S. Haz un resumen claro, técnico y directo de este correo en un solo párrafo:\n\n{cuerpo[:2000]}"
            try:
                respuesta_resumen = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt_resumen}])
                return f"Resumen del correo {indice + 1}:\n{respuesta_resumen['message']['content']}"
            except Exception as e:
                return f"Error en el motor local al resumir: {str(e)}"
            
        elif "correo" in texto_limpio or "gmail" in texto_limpio or "correos" in texto_limpio:
            if "busca correos de " in texto_limpio:
                remitente = texto_limpio.split("busca correos de ")[-1].strip()
                correos = self.gmail.obtener_correos(busqueda_libre=f"from:{remitente}")
                return f"Buscando los últimos correos del remitente '{remitente}':{correos}"
                
            elif "busca correos sobre " in texto_limpio:
                tema = texto_limpio.split("busca correos sobre ")[-1].strip()
                correos = self.gmail.obtener_correos(busqueda_libre=f'"{tema}"')
                return f"Buscando los últimos correos sobre el tema '{tema}':{correos}"
                
            else:
                incluir_todo = any(palabra in texto_limpio for palabra in ["anuncios", "spam", "todos", "sin filtro"])
                solo_no_leidos = any(palabra in texto_limpio for palabra in ["sin leer", "nuevos", "pendientes"])
                correos = self.gmail.obtener_correos(solo_no_leidos=solo_no_leidos, incluir_todo=incluir_todo)
                tipo_filtro = "sin filtros de categoría" if incluir_todo else "de su bandeja principal"
                estado_filtro = "pendientes" if solo_no_leidos else "recientes"
                return f"Revisando sus correos {estado_filtro} {tipo_filtro}. Esto es lo que he encontrado:{correos}"
            
        return None

    def _procesar_creacion_evento(self, texto):
        hoy = datetime.now()
        fecha_actual = hoy.strftime("%Y-%m-%d")
        dia_semana = hoy.strftime("%A")
        
        prompt_sistema = f"""Eres el analizador de datos de J.A.R.V.I.S.
Hoy es {dia_semana}, {fecha_actual}.
Extrae los datos del evento y devuelve ÚNICAMENTE un JSON válido, sin texto adicional y sin markdown.
Formato requerido:
{{
    "resumen": "Título corto del evento",
    "fecha": "YYYY-MM-DD",
    "hora_inicio": "HH:MM",
    "hora_fin": "HH:MM (Calcula la hora de fin si el usuario la menciona, si no, déjalo vacío)",
    "ubicacion": "Lugar específico o vacío si no hay"
}}
Si no especifica hora de inicio, asume "09:00"."""

        print("J.A.R.V.I.S.: [Procesando extracción de variables temporales con Llama 3.1...]")
        
        try:
            respuesta = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': texto}
            ])
            
            contenido = respuesta['message']['content'].strip()
            
            if contenido.startswith("```json"):
                contenido = contenido[7:-3].strip()
            elif contenido.startswith("```"):
                contenido = contenido[3:-3].strip()
                
            datos = json.loads(contenido)
            
            inicio_dt = datetime.strptime(f"{datos['fecha']} {datos['hora_inicio']}", "%Y-%m-%d %H:%M")
            
            hora_fin_str = datos.get('hora_fin', '').strip()
            if hora_fin_str:
                try:
                    fin_dt = datetime.strptime(f"{datos['fecha']} {hora_fin_str}", "%Y-%m-%d %H:%M")
                    if fin_dt <= inicio_dt:
                        fin_dt += timedelta(days=1)
                except ValueError:
                    fin_dt = inicio_dt + timedelta(hours=1)
            else:
                fin_dt = inicio_dt + timedelta(hours=1) 
            
            resultado = self.calendario.crear_evento(
                resumen=datos['resumen'], 
                inicio_dt=inicio_dt, 
                fin_dt=fin_dt, 
                ubicacion=datos.get('ubicacion', '')
            )
            return resultado
            
        except Exception as e:
            return f"He tenido un problema procesando las coordenadas temporales del evento: {e}"

    def _procesar_eliminacion_evento(self, texto):
        prompt_sistema = """Eres el analizador de datos de J.A.R.V.I.S.
El usuario quiere eliminar o cancelar un evento de su calendario.
Extrae el concepto, título o palabra clave principal del evento que quiere borrar y devuelve ÚNICAMENTE un JSON válido.
Formato requerido:
{
    "titulo_a_borrar": "Palabra clave del evento (ej: 'tutoria', 'examen de física', 'dentista')"
}"""

        print("J.A.R.V.I.S.: [Procesando extracción de evento a eliminar con Llama 3.1...]")
        
        try:
            respuesta = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': texto}
            ])
            
            contenido = respuesta['message']['content'].strip()
            
            if contenido.startswith("```json"):
                contenido = contenido[7:-3].strip()
            elif contenido.startswith("```"):
                contenido = contenido[3:-3].strip()
                
            datos = json.loads(contenido)
            titulo = datos.get("titulo_a_borrar", "").strip()
            
            if titulo:
                # Pasamos la palabra clave a las manos para que la busquen y la eliminen
                return self.calendario.eliminar_evento(titulo)
            else:
                return "No he podido identificar qué evento desea eliminar, señor."
                
        except Exception as e:
            return f"He tenido un problema procesando la orden de eliminación: {e}"

    def _procesar_temporizador(self, texto):
        # Buscamos cualquier número en tu frase usando Expresiones Regulares
        numeros = re.findall(r'\d+', texto)
        
        if not numeros:
            return "Por favor, especifique el tiempo numérico. Por ejemplo: 'temporizador de 5 minutos'."
            
        cantidad = int(numeros[0])
        segundos = 0
        texto_limpio = texto.lower()
        
        # Detectamos la unidad de tiempo
        if "hora" in texto_limpio:
            segundos = cantidad * 3600
            unidad = "horas" if cantidad > 1 else "hora"
        elif "segundo" in texto_limpio:
            segundos = cantidad
            unidad = "segundos" if cantidad > 1 else "segundo"
        else: 
            # Si no especifica, asumimos minutos por defecto
            segundos = cantidad * 60
            unidad = "minutos" if cantidad > 1 else "minuto"
            
        # Esta es la función que se ejecutará cuando el tiempo se agote
        def hacer_sonar_alarma():
            print(f"\nJ.A.R.V.I.S.: [¡ALARMA! EL TEMPORIZADOR DE {cantidad} {unidad.upper()} HA FINALIZADO]")
            # Hacemos sonar 5 pitidos de alerta (Frecuencia 2500Hz, Duración 500ms)
            for _ in range(5):
                return f"Tiempos"
                
        # Lanzamos el temporizador en un hilo secundario para que J.A.R.V.I.S. pueda seguir escuchándote
        threading.Timer(segundos, hacer_sonar_alarma).start()
        
        return f"Temporizador interno iniciado. Le avisaré en {cantidad} {unidad}."