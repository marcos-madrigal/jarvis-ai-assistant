import caldav
from datetime import datetime, timedelta
import uuid # <-- NUEVO: Generador de códigos únicos

class GestorCalendario:
    def __init__(self, correo_icloud, password_app):
        self.url = "https://caldav.icloud.com"
        self.usuario = correo_icloud
        self.password = password_app

    def obtener_eventos(self, dias=7):
        try:
            cliente = caldav.DAVClient(url=self.url, username=self.usuario, password=self.password)
            principal = cliente.principal()
            calendarios = principal.calendars()

            if not calendarios:
                return "No he podido encontrar calendarios en su cuenta de iCloud."

            inicio = datetime.now()
            fin = inicio.replace(hour=23, minute=59, second=59, microsecond=0)
            
            if dias > 1:
                fin += timedelta(days=dias - 1)

            eventos_encontrados = []

            for calendario in calendarios:
                try:
                    eventos = calendario.date_search(start=inicio, end=fin, expand=True)
                    for evento in eventos:
                        if hasattr(evento, 'icalendar_instance') and evento.icalendar_instance:
                            for componente in evento.icalendar_instance.walk('vevent'):
                                resumen = str(componente.get('summary', 'Sin título'))
                                dtstart = componente.get('dtstart').dt
                                
                                ubicacion_cruda = componente.get('location')
                                texto_ubicacion = f" | 📍 Ubicación: {str(ubicacion_cruda)}" if ubicacion_cruda else ""
                                
                                if isinstance(dtstart, datetime):
                                    fecha_str = dtstart.strftime("%d/%m/%Y %H:%M")
                                else:
                                    fecha_str = dtstart.strftime("%d/%m/%Y (Todo el día)")
                                    
                                eventos_encontrados.append((dtstart, f"- {resumen} ({fecha_str}){texto_ubicacion}"))
                except Exception:
                    continue
            
            if not eventos_encontrados:
                return f"No tiene eventos programados en los próximos {dias} días, señor."

            def limpiar_zona_horaria(dt):
                if isinstance(dt, datetime):
                    return dt.replace(tzinfo=None)
                return datetime.combine(dt, datetime.min.time())

            eventos_encontrados.sort(key=lambda x: limpiar_zona_horaria(x[0]))
            
            texto_eventos = "\n".join([e[1] for e in eventos_encontrados])
            return f"Eventos programados:\n{texto_eventos}"

        except Exception as e:
            return f"Error en la conexión con iCloud: {str(e)}"

    def crear_evento(self, resumen, inicio_dt, fin_dt, ubicacion=""):
        """Inyecta un nuevo evento en iCloud usando el protocolo iCalendar estricto"""
        try:
            cliente = caldav.DAVClient(url=self.url, username=self.usuario, password=self.password)
            principal = cliente.principal()
            calendarios = principal.calendars()

            if not calendarios:
                return "Error: No he podido acceder a sus calendarios para escribir."

            # Usaremos el primer calendario, pero imprimiremos su nombre para saber cuál es
            calendario_destino = calendarios[0]
            print(f"J.A.R.V.I.S.: [Guardando evento en el calendario '{calendario_destino.name}']")

            # 1. Generamos los metadatos obligatorios para Apple
            uid_evento = str(uuid.uuid4())
            # DTSTAMP debe ser en hora UTC y terminar en Z (Zulu)
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            
            # Formateamos las fechas de inicio y fin
            inicio_str = inicio_dt.strftime("%Y%m%dT%H%M%S")
            fin_str = fin_dt.strftime("%Y%m%dT%H%M%S")
            
            # 2. Construimos el payload estricto
            paquete_vcal = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//JARVIS//SistemaLocal//ES
BEGIN:VEVENT
UID:{uid_evento}
DTSTAMP:{dtstamp}
SUMMARY:{resumen}
DTSTART;TZID=Europe/Madrid:{inicio_str}
DTEND;TZID=Europe/Madrid:{fin_str}
LOCATION:{ubicacion}
END:VEVENT
END:VCALENDAR"""

            # 3. Enviamos el paquete
            calendario_destino.save_event(paquete_vcal)
            
            texto_lugar = f" en {ubicacion}" if ubicacion else ""
            return f"He programado '{resumen}' para el {inicio_dt.strftime('%d/%m/%Y a las %H:%M')}{texto_lugar}."

        except Exception as e:
            return f"Error en la base de datos de iCloud al crear el evento: {str(e)}"

    def eliminar_evento(self, nombre_evento):
        """Busca un evento por nombre en los próximos 30 días y lo elimina de iCloud"""
        try:
            cliente = caldav.DAVClient(url=self.url, username=self.usuario, password=self.password)
            principal = cliente.principal()
            calendarios = principal.calendars()

            if not calendarios:
                return "Error: No he podido acceder a sus calendarios."

            # Buscamos desde hoy a medianoche hasta dentro de 30 días
            inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            fin = inicio + timedelta(days=30)

            print(f"J.A.R.V.I.S.: [Buscando '{nombre_evento}' para eliminarlo...]")

            for calendario in calendarios:
                try:
                    eventos = calendario.date_search(start=inicio, end=fin, expand=True)
                    for evento in eventos:
                        if hasattr(evento, 'icalendar_instance') and evento.icalendar_instance:
                            for componente in evento.icalendar_instance.walk('vevent'):
                                resumen = str(componente.get('summary', '')).lower()
                                
                                # Si el nombre del evento que buscamos está dentro del título del evento real
                                if nombre_evento.lower() in resumen:
                                    titulo_real = str(componente.get('summary', ''))
                                    evento.delete() # <--- LA ORDEN DE DESTRUCCIÓN
                                    return f"He eliminado con éxito el evento '{titulo_real}' de su agenda."
                except Exception:
                    continue
            
            return f"No he encontrado ningún evento relacionado con '{nombre_evento}' en los próximos 30 días."

        except Exception as e:
            return f"Error al intentar eliminar el evento en iCloud: {str(e)}"