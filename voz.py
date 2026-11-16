import os
# Ocultamos el mensaje de bienvenida de pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import speech_recognition as sr
import edge_tts
import asyncio
import pygame

class GestorVoz:
    def __init__(self):
        # Inicializamos el motor de audio independiente
        pygame.mixer.init()
        
        # --- OÍDOS (STT Gratuito) ---
        self.reconocedor = sr.Recognizer()
        self.reconocedor.pause_threshold = 2.0
        self.reconocedor.non_speaking_duration = 1.5
        self.reconocedor.dynamic_energy_threshold = True
        self.microfono = sr.Microphone()

    def hablar(self, texto):
        """Genera voz neuronal ultra realista y la reproduce"""
        # 1. Texto para la pantalla
        texto_visual = texto.replace('*', '').replace('#', '')
        print(f"J.A.R.V.I.S.: {texto_visual}")
        
        # 2. Texto para hablar (limpiamos el emoji)
        texto_hablado = texto_visual.replace('📍', 'en el aula')
        
        try:
            # Generamos el audio con la voz neuronal de Álvaro (Acento de España)
            comunicar = edge_tts.Communicate(texto_hablado, "es-ES-AlvaroNeural")
            asyncio.run(comunicar.save("temp_voz.mp3"))
            
            # Reproducimos el archivo de forma segura
            pygame.mixer.music.load("temp_voz.mp3")
            pygame.mixer.music.play()
            
            # Esperamos a que termine de hablar para volver a escuchar
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Liberamos el archivo de la memoria
            pygame.mixer.music.unload()
            
        except Exception as e:
            print(f"[Error reproduciendo voz neuronal: {e}]")

    def escuchar(self):
        """Escucha el micrófono con autocalibración en tiempo real"""
        with self.microfono as origen:
            self.reconocedor.adjust_for_ambient_noise(origen, duration=0.5)
            print("\nJ.A.R.V.I.S.: [Micrófono abierto. Te escucho...]")
            try:
                audio = self.reconocedor.listen(origen, timeout=5, phrase_time_limit=20)
                texto = self.reconocedor.recognize_google(audio, language="es-ES")
                print(f"Tú: {texto}")
                return texto
            
            except sr.WaitTimeoutError:
                return "" 
            except sr.UnknownValueError:
                print("J.A.R.V.I.S.: [He detectado ruido, pero no entendí las palabras]")
                return ""
            except sr.RequestError:
                print("J.A.R.V.I.S.: [Error de conexión de red en el micrófono]")
                return ""
            except Exception:
                return ""