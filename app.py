from flask import Flask, render_template, request, jsonify
from jarvis import JarvisCore
import os
import threading

app = Flask(__name__)
asistente = JarvisCore()

def apagar_servidor():
    """Fuerza el cierre del proceso de Python en el sistema operativo"""
    print("\n[Servidor desconectado por orden del usuario]")
    os._exit(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.json
    mensaje_usuario = datos.get('mensaje', '')
    
    # 1. Interceptamos los comandos de apagado
    comandos_apagado = ['salir', 'apagar', 'exit', 'adiós', 'adios', 'gracias adios']
    
    if mensaje_usuario.lower().strip() in comandos_apagado:
        # Programamos la "autodestrucción" para dentro de 1 segundo
        threading.Timer(1.0, apagar_servidor).start()
        # Le respondemos a la interfaz visual justo antes de morir
        return jsonify({"respuesta": "Apagando sistemas. Que tenga un excelente día, señor."})
    
    # 2. Si no es un comando de apagado, procesa de forma normal
    respuesta = asistente.procesar(mensaje_usuario)
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    print("Iniciando Servidor Interfaz J.A.R.V.I.S...")
    app.run(debug=True, port=5000)